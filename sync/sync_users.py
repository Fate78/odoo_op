import logging
from odoo import models, exceptions
import hashlib
from datetime import datetime

_logger = logging.getLogger(__name__)


class NonStopException(exceptions.UserError):
    """Will bypass the record"""


class SyncUsers(models.AbstractModel):
    _name = 'sync.users'
    _description = 'Synchronize Users'
    hashed_project = hashlib.sha256()
    hashed_op_project = hashlib.sha256()
    limit = 5

    @staticmethod
    def get_hashed(_id, _firstname, _lastname, _login, _email, _admin):
        hashable = str(_id) + _firstname + _lastname + _login + _email + str(_admin)
        hashed = hashlib.md5(hashable.encode("utf-8")).hexdigest()
        print("Inside Hash: ", hashed)
        return hashed

    def cron_sync_users(self):
        env_user = self.env['op.user']
        main_url = env_user.get_users_url()
        users = env_user.get_data_to_update('op.user', self.limit)
        response = env_user.get_response(main_url)
        next_offset = True
        while next_offset:
            for r in response['_embedded']['elements']:
                user_search_id = env_user.search([['db_id', '=', r['id']]])
                _id = r['id']
                _firstname = r['firstName']
                _lastname = r['lastName']
                _login = r['login']
                _email = r['email']
                _admin = r['admin']
                if user_search_id.exists():
                    for u in users:
                        if u.db_id == _id:
                            hashed_user = self.get_hashed(u.db_id, u.firstname, u.lastname, u.login, u.email, u.admin)
                            hashed_op_user = self.get_hashed(_id, _firstname, _lastname, _login, _email, _admin)

                            if hashed_user != hashed_op_user:
                                try:
                                    print("Updating user: %s\n" % u.db_id)
                                    values = {
                                        'firstname': _firstname,
                                        'lastname': _lastname,
                                        'login': _login,
                                        'email': _email,
                                        'admin': _admin
                                    }
                                    self.env.cr.savepoint()
                                    user_search_id.write(values)
                                except NonStopException as e:
                                    _logger.error('Bypass Error: %s' % e)
                                    continue
                                except Exception as e:
                                    _logger.error('Error: %s' % e)
                                    self.env.cr.rollback()
                            else:
                                print("User up to date: %s\n" % _id)
                                user_search_id.write({'write_date': datetime.now()})
                                # Updating write_date to know it has been looked through
                else:
                    try:
                        print("Creating user: %s\n" % _id)
                        values = {
                            'db_id': _id,
                            'firstname': _firstname,
                            'lastname': _lastname,
                            'login': _login,
                            'email': _email,
                            'admin': _admin
                        }
                        self.env.cr.savepoint()
                        users.create(values)
                    except Exception as e:
                        print("Exception has occurred: ", e)
                        print("Exception type: ", type(e))
                        self.env.cr.rollback()
            self.env.cr.commit()
            print("All data committed")
            next_offset, response = env_user.check_next_offset(response)
