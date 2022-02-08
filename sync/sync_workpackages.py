from requests.models import HTTPBasicAuth
from odoo import models, fields, api
from odoo.exceptions import UserError
import json
import hashlib
from datetime import datetime
import isodate
import json
import logging

_logger = logging.getLogger(__name__)


class NonStopException(UserError):
    """Will bypass the record"""


class SyncWorkPackages(models.AbstractModel):

    _name = 'sync.workpackages'
    _description = 'Synchronize Work Packages'
    hashed_wp = hashlib.sha256()
    hashed_op_wp = hashlib.sha256()
    limit=20

    def get_hashed(self,_id,project_id,name,description,spent_time,author_id,responsible_id):
        hashable=json.dumps(_id) + json.dumps(project_id) + name + description + json.dumps(spent_time) + str(author_id) + str(responsible_id)
        hashed=hashlib.md5(hashable.encode("utf-8")).hexdigest()
        return hashed
    
    def cron_sync_workpackages(self):
        #Loop through every project
        env_work_package = self.env['op.work.package']
        env_project = self.env['op.project']
        projects_url = env_project.get_projects_url()
        response = env_project.get_response(projects_url)
        next_offset_project = True
        while next_offset_project:
            for r in response['_embedded']['elements']:
                _id_project = r['id']
                _active = r['active']
                main_url = env_work_package.get_project_workpackages_url(_id_project)
                response_work_package = env_work_package.get_response(main_url)
                next_offset_wp = True
                
                while next_offset_wp:
                    if(_active!=False):
                        for rw in response_work_package['_embedded']['elements']:
                            _id = rw['id']
                            _name = rw['subject']
                            _spentTime = isodate.parse_duration(rw['spentTime'])
                            _string_spentTime = str(_spentTime)
                            _int_spentTime = env_work_package.get_timeFloat(_string_spentTime)
                            _description = rw['description']['raw']
                            _author_id = env_work_package.get_id_href(rw['_links']['author']['href'])
                            _responsible_id = rw['_links']['responsible']['href']

                            if(_responsible_id!=None):
                                _responsible_id = env_work_package.get_id_href(rw['_links']['responsible']['href'])

                            work_packages=env_work_package.get_data_to_update('op.work.package',self.limit)
                            work_package_search_id=env_work_package.search([['db_id','=',_id]])
                            
                            if(work_package_search_id.exists()):
                                for w in work_packages:
                                    if(w.db_id==_id):
                                        w_db_id=w.db_id
                                        w_db_project_id=w.db_project_id
                                        w_name=w.name
                                        w_description=env_work_package.verify_field_empty(w.description)
                                        w_spent_time=w.spent_time
                                        w_db_author_id=w.db_author_id
                                        w_db_responsible_id=env_work_package.verify_field_empty(w.db_responsible_id)
                                        
                                        _description=env_work_package.verify_field_empty(_description)
                                        _responsible_id=env_work_package.verify_field_empty(_responsible_id)
                                        
                                        hashed_wp = self.get_hashed(w_db_id,w_db_project_id,w_name,w_description,w_spent_time,w_db_author_id,w_db_responsible_id)
                                        print(w_db_id,w_db_project_id,w_name,w_description,w_spent_time,w_db_author_id,w_db_responsible_id)
                                        print(hashed_wp)
                                        
                                        hashed_op_wp = self.get_hashed(_id,_id_project,_name,_description,_int_spentTime,_author_id,_responsible_id)
                                        print(_id,_id_project,_name,_description,_int_spentTime,_author_id,_responsible_id)
                                        print(hashed_op_wp)
                                        if(hashed_wp!=hashed_op_wp):
                                            try:
                                                print("Updating Workpackage...\n")
                                                vals = {
                                                    'db_project_id':_id_project,
                                                    'name':_name,
                                                    'description':_description,
                                                    'spent_time':_int_spentTime,
                                                    'db_author_id':_author_id,
                                                    'db_responsible_id':_responsible_id
                                                }
                                                work_package_search_id.write(vals)
                                            except NonStopException:
                                                _logger.error('Bypass Error: %s' % e)
                                                continue
                                            except Exception as e:
                                                _logger.error('Error: %s' % e)
                                                self.env.cr.rollback()
                                        else:
                                            print("Workpackage up to date\n")
                                            work_package_search_id.write({'write_date':datetime.now()})
                            else:
                                try:
                                    print("Creating workpackage...\n")
                                    vals = {
                                        'db_id':_id,
                                        'db_project_id':_id_project,
                                        'name':_name,
                                        'description':_description,
                                        'spent_time':_int_spentTime,
                                        'db_author_id':_author_id,
                                        'db_responsible_id':_responsible_id
                                    }
                                    work_packages.create(vals)
                                except Exception as e:
                                    print("Exception has ocurred: ", e)
                                    print("Exception type: ", type(e))
                            next_offset_wp, response_work_package = env_project.check_next_offset(next_offset_wp, response_work_package) #check if wp next_offset exists
                else:
                    print("Permission denied to project %d" % (_id_project))
            self.env.cr.commit()
            print("All data commited")
            next_offset_project, response = env_project.check_next_offset(next_offset_project, response) #check if project next_offset exists