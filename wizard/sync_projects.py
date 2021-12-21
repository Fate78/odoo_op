from requests.models import HTTPBasicAuth
import logging
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import requests
import json
import hashlib
from base64 import b64encode
from pprint import pprint
from datetime import datetime
from datetime import timedelta
from dateutil import parser

_logger = logging.getLogger(__name__)

class NonStopException(UserError):
    """Will bypass the record"""

class SyncProjects(models.TransientModel):
    _name = 'sync.projects'
    _description = 'Synchronize Projects'
    hashed_project = hashlib.sha256()
    hashed_op_project = hashlib.sha256()
    limit=10
    

    def get_hashed(self,_id,identifier,name,public):
        hashable=json.dumps(_id) + identifier + name + json.dumps(public)
        print("Inside Hash: ", _id,identifier)
        hashed=hashlib.md5(hashable.encode("utf-8")).hexdigest()
        return hashed

    def cron_sync_projects(self):
        main_url = self.env['op.project'].get_projects_url()
        projects = self.env['op.project'].get_data_to_update('op.project',self.limit)
        response = self.env['op.project'].get_response(main_url)
        for r in response['_embedded']['elements']:
            project_search_id=self.env['op.project'].search([['db_id','=',r['id']]])
            _id = r['id']
            _identifier = r['identifier']
            _name = r['name']
            archived = r['active']
            dt_createdAt = parser.parse(r['createdAt'])
            dt_updatedAt = parser.parse(r['updatedAt'])
            _public = r['public']
            if(project_search_id.exists()):
                #Se os projetos com certa data não existirem ele não entra no for
                for p in projects:
                    if(p.db_id == _id):
                        print("Before Hash: ", p.db_id,p.op_identifier)
                        hashed_project = self.get_hashed(p.db_id,p.op_identifier,p.name,p.public)
                        hashed_op_project = self.get_hashed(_id,_identifier,_name,_public)
                        print("project: ",p.db_id)
                        print(hashed_project)
                        print(p.db_id)
                        print(hashed_op_project)
                        print(_id)
                        if(hashed_project!=hashed_op_project):
                            try:
                                print("Updating project: %s\n"%(p.db_id))
                                vals = {
                                    'op_identifier':_identifier,
                                    'name':_name,
                                    'public':_public
                                    }
                                project_search_id.write(vals)
                            except NonStopException:
                                _logger.error('Bypass Error: %s' % e)
                                continue
                            except Exception as e:
                                _logger.error('Error: %s' % e)
                                self.env.cr.rollback()
                        else:
                            print("Project up to date: %s\n"%(_id))
                            project_search_id.write({'write_date':datetime.now()})
                            #Updating write_date to know it has been looked through
            else:
                try:
                    print("Creating project: %s\n"%(_id))
                    vals = {
                        'db_id':_id,
                        'op_identifier':_identifier,
                        'name':_name,
                        'public':_public
                    }
                    projects.create(vals)
                except Exception as e:
                    print("Exception has ocurred: ", e)
                    print("Exception type: ", type(e))
        self.env.cr.commit()
        print("All data commited")