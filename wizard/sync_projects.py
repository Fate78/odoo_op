from requests.models import HTTPBasicAuth
from odoo import models, fields, api
import requests
import json
import hashlib
from base64 import b64encode
from pprint import pprint
from datetime import datetime
from datetime import timedelta
from dateutil import parser

class SyncProjects(models.TransientModel):
    _name = 'sync.projects'
    _description = 'Synchronize Projects'
    base_path = "http://localhost:3000"
    endpoint_url = "/api/v3/projects/"
    hashed_project = hashlib.sha256()
    hashed_op_project = hashlib.sha256()
    limit=50
    main_url = "%s%s" % (base_path,endpoint_url)

    def get_hashed(self,_id,identifier,name,public):
        hashable=json.dumps(_id) + identifier + name + json.dumps(public)
        hashed=hashlib.md5(hashable.encode("utf-8")).hexdigest()
        return hashed

    def cron_sync_projects(self):
        projects = self.env['op.project'].get_data_to_update('op.project',self.limit)
        response = self.env['op.project'].get_response(self.main_url)
        for r in response['_embedded']['elements']:
            project_search_id=self.env['op.project'].search([['db_id','=',r['id']]])
            _id = r['id']
            _identifier = r['identifier']
            _name = r['name']
            archived = r['active']
            dt_createdAt = parser.parse(r['createdAt'])
            dt_updatedAt = parser.parse(r['updatedAt'])
            _public = r['public']
            # If exists hash it
            if(project_search_id.exists()):
                #Se os projetos com certa data não existirem ele não entra no for
                try:
                    for p in projects:
                        if(p.db_id == _id):
                            hashed_project = self.get_hashed(p.db_id,p.op_identifier,p.name,p.public)
                            hashed_op_project = self.get_hashed(_id,_identifier,_name,_public)
                            print(hashed_project)
                            print(hashed_op_project)
                            if(hashed_project!=hashed_op_project):
                                    print("Updating project: %s\n"%(p.db_id))
                                    vals = {
                                        'db_id':_id,
                                        'op_identifier':_identifier,
                                        'name':_name,
                                        'public':_public
                                        }
                                    projects.write(vals)
                            else:
                                print("Project up to date: %s\n"%(_id))
                                projects.write({'write_date':datetime.now()})
                                #Update write_date to know it has been looked through
                except Exception as e:
                    print("Exception has ocurred: ", e)
                    print("Exception type: ", type(e))
                    self.env.cr.rollback()
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
                    self.env.cr.rollback()
        self.env.cr.commit()
        print("All data commited")