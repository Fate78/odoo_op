import isodate
import logging
from odoo import models, exceptions
import hashlib
from datetime import datetime

_logger = logging.getLogger(__name__)


class NonStopException(exceptions.UserError):
    """Will bypass the record"""


class SyncTimeEntries(models.AbstractModel):
    _name = 'sync.time_entries'
    _description = 'Synchronize Time Entries'
    hashed_time_entry = hashlib.sha256()
    hashed_op_time_entry = hashlib.sha256()
    limit = 5

    @staticmethod
    def get_hashed(_id, _project_id, _user_id, _work_package_id, _activity_id, _hours, _spentOn, _comment):
        hashable = str(_id) + str(_project_id) + str(_user_id) + str(_work_package_id) + str(_activity_id) + str(
            _hours) + str(_spentOn) + _comment
        hashed = hashlib.md5(hashable.encode("utf-8")).hexdigest()
        print("Inside Hash: ", hashed)
        return hashed

    def cron_sync_time_entries(self):
        env_time_entry = self.env['op.time.entry']
        main_url = env_time_entry.get_time_entries_url()
        time_entries = env_time_entry.get_data_to_update('op.time.entry', self.limit)
        response = env_time_entry.get_response(main_url)
        next_offset = True
        while next_offset:
            for r in response['_embedded']['elements']:
                time_entry_search_id = env_time_entry.search([['db_id', '=', r['id']]])
                _id = r['id']
                _comment = r['comment']['raw']
                _project_id = env_time_entry.get_id_href(r['_links']['project']['href'])
                _user_id = env_time_entry.get_id_href(r['_links']['user']['href'])
                _work_package_id = env_time_entry.get_id_href(r['_links']['workPackage']['href'])
                _activity_id = env_time_entry.get_id_href(r['_links']['activity']['href'])
                _spentOn = r['spentOn']  # string date
                _spentOn_date = datetime.strptime(_spentOn, "%Y-%m-%d")
                _hours = r['hours']  # iso
                _hours_float = env_time_entry.get_time_float(str(isodate.parse_duration(_hours)))

                if time_entry_search_id.exists():
                    for t in time_entries:
                        if t.db_id == _id:
                            t_db_id = t.db_id
                            t_db_project_id = str(t.db_project_id)
                            t_db_user_id = t.db_user_id
                            t_db_work_package_id = t.db_work_package_id
                            t_db_activity_id = t.db_activity_id
                            t_op_hours = t.op_hours
                            t_op_spent_on = t.op_spent_on
                            t_comment = env_time_entry.verify_field_empty(t.comment)
                            _comment = env_time_entry.verify_field_empty(_comment)

                            hashed_time_entry = self.get_hashed(t_db_id, t_db_project_id, t_db_user_id,
                                                                t_db_work_package_id,
                                                                t_db_activity_id, t_op_hours, t_op_spent_on, t_comment)
                            hashed_op_time_entry = self.get_hashed(_id, _project_id, _user_id, _work_package_id,
                                                                   _activity_id,
                                                                   _hours_float, _spentOn, _comment)

                            if hashed_time_entry != hashed_op_time_entry:
                                try:
                                    print("Updating Time Entry: %s\n" % t.db_id)
                                    values = {
                                        'db_project_id': _project_id,
                                        'db_user_id': _user_id,
                                        'db_work_package_id': _work_package_id,
                                        'db_activity_id': _activity_id,
                                        'op_hours': _hours_float,
                                        'op_spent_on': _spentOn_date,
                                        'comment': _comment
                                    }
                                    self.env.cr.savepoint()
                                    time_entry_search_id.write(values)
                                except NonStopException as e:
                                    _logger.error('Bypass Error: %s' % e)
                                    continue
                                except Exception as e:
                                    _logger.error('Error: %s' % e)
                                    self.env.cr.rollback()
                            else:
                                print("Time Entry up to date: %s\n" % _id)
                                time_entry_search_id.write({'write_date': datetime.now()})
                                # Updating write_date to know it has been looked through
                else:
                    try:
                        print("Creating Time Entry: %s\n" % _id)
                        values = {
                            'db_id': _id,
                            'db_project_id': _project_id,
                            'db_user_id': _user_id,
                            'db_work_package_id': _work_package_id,
                            'db_activity_id': _activity_id,
                            'op_hours': _hours_float,
                            'op_spent_on': _spentOn_date,
                            'comment': _comment
                        }
                        self.env.cr.savepoint()
                        time_entries.create(values)
                    except Exception as e:
                        print("Exception has occurred: ", e)
                        print("Exception type: ", type(e))
                        self.env.cr.rollback()
            self.env.cr.commit()
            print("All data committed")
            next_offset, response = env_time_entry.check_next_offset(response)
