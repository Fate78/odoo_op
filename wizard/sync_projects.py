from requests.models import HTTPBasicAuth
from odoo import models, fields, api
from odoo.exceptions import UserError
import requests
import json
import hashlib
from base64 import b64encode
from pprint import pprint
from datetime import datetime
from dateutil import parser

#TODO
#Query the database in batches
#

class SyncProjects(models.TransientModel):
    _name = 'sync.projects'
    _description = 'Synchronize Projects'
    base_path = "http://localhost:3000"
    endpoint_url = "/api/v3/projects/"
    hashed_project = hashlib.sha256()
    hashed_op_project = hashlib.sha256()

    def get_api_key(self):
        api_key = self.env['ir.config_parameter'].sudo().get_param('openproject.api_key') or False
        return api_key
    
    def get_response(self,url):
        api_key=self.get_api_key()
        
        resp = requests.get(
            url,
            auth=('apikey', api_key)
            )
        return json.loads(resp.text)

    def cron_sync_projects(self):
        
        main_url = "%s%s" % (self.base_path, self.endpoint_url)

        response = self.get_response(main_url)

        while response['_links']['nextByOffset']['href']:
            for r in response['_embedded']['elements']:
                _id = r['id']
                _identifier = r['identifier']
                _name = r['name']
                archived = r['active']
                dt_createdAt = parser.parse(r['createdAt'])
                dt_updatedAt = parser.parse(r['updatedAt'])
                _public = r['public']
                string_op_id = json.dumps(_id)
                string_op_public = json.dumps(_public) 
                hashable_op_project = string_op_id + _identifier + _name + string_op_public
                
                #Search data and hash it
                projects=self.env['op.project'].search([['db_id','=',_id]])
                #If exists
                if(projects.exists()):
                    project_id = json.dumps(projects.db_id)
                    project_public = json.dumps(projects.public)
                    hashable_project = project_id + projects.op_identifier + projects.name + project_public

                    hashed_project = hashlib.md5(hashable_project.encode("utf-8")).hexdigest()
                    hashed_op_project = hashlib.md5(hashable_op_project.encode("utf-8")).hexdigest()
                    print("project_identifier: ", projects.op_identifier)

                    print(hashed_project)
                    print(hashed_op_project)

                    if(hashed_project!=hashed_op_project):
                        try:
                            print("Updating project...\n")
                            vals = {
                                'db_id':_id,
                                'op_identifier':_identifier,
                                'name':_name,
                                'public':_public
                                }
                            projects.write(vals)
                        except Exception as e:
                            print("Exception has ocurred: ", e)
                            print("Exception type: ", type(e))
                    else:
                        print("Project up to date\n")
                else:
                    try:
                        print("Creating project...\n")
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
            
            #Check 50 items if they have an id
            #If they dont, create them
            #If they do compare hashes

            # for index in range(0, len(values)):
            #     #print(f"\n\n {values[index]} \n\n")
            #     print(f"\n {values[0]} \n")

            #Insert or Update odoo db with op data if old_hash = new_hash
            #Check if id exists in odoo if not insert if yes update
            