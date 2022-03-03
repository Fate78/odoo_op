import logging
from odoo import models, exceptions
import hashlib
from datetime import datetime

_logger = logging.getLogger(__name__)


class NonStopException(exceptions.UserError):
    """Will bypass the record"""


class SyncProjects(models.AbstractModel):
    _name = 'sync.projects'
    _description = 'Synchronize Projects'
    hashed_project = hashlib.sha256()
    hashed_op_project = hashlib.sha256()
    limit = 20

    @staticmethod
    def get_hashed(_id, identifier, name, public, description, active):
        hashable = str(_id) + identifier + name + str(public) + description + str(active)
        hashed = hashlib.md5(hashable.encode("utf-8")).hexdigest()
        print("Inside Hash: ", hashed)
        return hashed

    def cron_sync_projects(self):
        env_project = self.env['op.project']
        main_url = env_project.get_projects_url()
        projects = env_project.get_data_to_update('op.project', self.limit)
        response = env_project.get_response(main_url)
        next_offset = True
        while next_offset:
            for r in response['_embedded']['elements']:
                project_search_id = env_project.search([['db_id', '=', r['id']]])
                _id = r['id']
                _identifier = r['identifier']
                _name = r['name']
                _description = r['description']['raw']
                _active = r['active']
                _public = r['public']
                if project_search_id.exists():
                    for p in projects:
                        if p.db_id == _id:
                            p_db_id = p.db_id
                            p_op_identifier = p.op_identifier
                            p_name = p.name
                            p_public = p.public
                            p_active = p.active
                            p_description = env_project.verify_field_empty(p.description)
                            _description = env_project.verify_field_empty(
                                _description)  # Initialize description if it's None

                            hashed_project = self.get_hashed(p_db_id, p_op_identifier, p_name, p_public, p_description,
                                                             p_active)
                            hashed_op_project = self.get_hashed(_id, _identifier, _name, _public, _description, _active)

                            if hashed_project != hashed_op_project:
                                try:
                                    print("Updating project: %s\n" % p.db_id)
                                    values = {
                                        'op_identifier': _identifier,
                                        'name': _name,
                                        'public': _public,
                                        'description': _description,
                                        'active': _active
                                    }
                                    project_search_id.write(values)
                                except NonStopException as e:
                                    _logger.error('Bypass Error: %s' % e)
                                    continue
                                except Exception as e:
                                    _logger.error('Error: %s' % e)
                                    self.env.cr.rollback()
                            else:
                                print("Project up to date: %s\n" % _id)
                                project_search_id.write({'write_date': datetime.now()})
                                # Updating write_date to know it has been looked through
                else:
                    try:
                        print("Creating project: %s\n" % _id)
                        values = {
                            'db_id': _id,
                            'op_identifier': _identifier,
                            'name': _name,
                            'public': _public,
                            'description': _description,
                            'active': _active
                        }
                        projects.create(values)
                    except Exception as e:
                        print("Exception has occurred: ", e)
                        print("Exception type: ", type(e))
            self.env.cr.commit()
            print("All data committed")
            next_offset, response = env_project.check_next_offset(response)
