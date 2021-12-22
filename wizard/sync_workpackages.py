from requests.models import HTTPBasicAuth
from odoo import models, fields, api
from odoo.exceptions import UserError
import requests
import json
import hashlib
from base64 import b64encode
from pprint import pprint
from dateutil import parser
from datetime import datetime
import isodate
import json
import logging

_logger = logging.getLogger(__name__)

class NonStopException(UserError):
    """Will bypass the record"""

class SyncWorkPackages(models.TransientModel):

    _name = 'sync.workpackages'
    _description = 'Synchronize Work Packages'
    hashed_wp = hashlib.sha256()
    hashed_op_wp = hashlib.sha256()
    limit=10

    def get_hashed(self,_id,project_id,name,spent_time):
        hashable=json.dumps(_id) + json.dumps(project_id) + name + json.dumps(spent_time)
        hashed=hashlib.md5(hashable.encode("utf-8")).hexdigest()
        return hashed

    def cron_sync_workpackages(self):
        #Loop through every project
        projects_url = self.env['op.project'].get_projects_url()
        response = self.env['op.project'].get_response(projects_url)
        for r in response['_embedded']['elements']:
            _id_project = r['id']
            _active = r['active']
            main_url = self.env['op.work.package'].get_project_workpackages_url(_id_project)
            response_work_package = self.env['op.work.package'].get_response(main_url)
            if(_active!=False):
                for rw in response_work_package['_embedded']['elements']:
                    _id = rw['id']
                    _name = rw['subject']
                    _spentTime = isodate.parse_duration(rw['spentTime'])
                    _string_spentTime = str(_spentTime)
                    _int_spentTime = self.env['op.work.package'].get_timeFloat(_string_spentTime)
                    work_packages=self.env['op.work.package'].get_data_to_update('op.work.package',self.limit)
                    work_package_search_id=self.env['op.work.package'].search([['db_id','=',_id]])
                    
                    if(work_package_search_id.exists()):
                        for w in work_packages:
                            if(w.db_id==_id):
                                hashed_wp = self.get_hashed(w.db_id,w.db_project_id,w.name,w.spent_time)
                                hashed_op_wp = self.get_hashed(_id,_id_project,_name,_int_spentTime)
                                print(hashed_wp)
                                print(hashed_op_wp)
                                if(hashed_wp!=hashed_op_wp):
                                    try:
                                        print("Updating version...\n")
                                        vals = {
                                            'db_project_id':_id_project,
                                            'name':_name,
                                            'spent_time':_int_spentTime
                                        }
                                        work_package_search_id.write(vals)
                                    except NonStopException:
                                        _logger.error('Bypass Error: %s' % e)
                                        continue
                                    except Exception as e:
                                        _logger.error('Error: %s' % e)
                                        self.env.cr.rollback()
                                else:
                                    print("Version up to date\n")
                                    work_package_search_id.write({'write_date':datetime.now()})
                    else:
                        try:
                            print("Creating version...\n")
                            vals = {
                                'db_id':_id,
                                'db_project_id':_id_project,
                                'name':_name,
                                'spent_time':_int_spentTime
                            }
                            work_packages.create(vals)
                        except Exception as e:
                            print("Exception has ocurred: ", e)
                            print("Exception type: ", type(e))
            else:
                print("Permission denied to project %d" % (_id_project))
        self.env.cr.commit()
        print("All data commited")