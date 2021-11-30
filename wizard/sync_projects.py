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

class InvalidDatabaseException(UserError):
    """An error ocurred in the database"""

class SyncProjects(models.TransientModel):
    _name = 'sync.projects'
    _description = 'Synchronize Projects'
    base_path = "http://localhost:8080"
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
        for r in response['_embedded']['elements']:
            project_id = r['id']
            project_identifier = r['identifier']
            project_name = r['name']
            archived = r['active']
            dt_createdAt = parser.parse(r['createdAt'])
            dt_updatedAt = parser.parse(r['updatedAt'])
            public = r['public']
            string_op_id = json.dumps(r['id'])
            string_op_public = json.dumps(r['public']) 
            hashable_op_project = string_op_id + project_identifier + project_name + string_op_public
            
            #Select data and hash it
            #id=0,identifier=6,name=7,public=8
            exists = self.env.cr.execute("""SELECT 1 FROM op_project WHERE id=%s"""%(project_id))
            
            #If exists
            if(self.env.cr.fetchone()!=None):
                self.env.cr.execute("""SELECT * FROM op_project WHERE id=%s"""%(project_id))
                projects_dict = self.env.cr.fetchall()
                string_id = json.dumps(projects_dict[0][0])
                string_public = json.dumps(projects_dict[0][8])

                hashable_project = string_id + projects_dict[0][6] + projects_dict[0][7] + string_public

                hashed_project = hashlib.md5(hashable_project.encode("utf-8")).hexdigest()
                hashed_op_project = hashlib.md5(hashable_op_project.encode("utf-8")).hexdigest()
                print("project_id: ", project_id)

                print(hashed_project)
                print(hashed_op_project)

                if(hashed_project!=hashed_op_project):
                    try:
                        print("Updating project...\n")
                        self.env.cr.execute("""UPDATE op_project
                                            SET op_identifier=%s, name=%s, public=%s
                                            WHERE op_project.id=%s
                                            RETURNING op_identifier""",
                                            (project_identifier, project_name, public, project_id))
                    except Exception as e:
                        print("Exception has ocurred: ", e)
                        print("Exception type: ", type(e))
                else:
                    print("Project up to date\n")
            else:
                try:
                    print("Creating project...\n")
                    self.env.cr.execute("""INSERT INTO op_project(id, op_identifier, name, public)
                                        VALUES (%s, %s, %s, %s)
                                        RETURNING op_identifier""",
                                    (project_id, project_identifier, project_name, public))
                except Exception as e:
                    print("Exception has ocurred: ", e)
                    print("Exception type: ", type(e))
            
            #Check 50 items if they have an id
            #If they dont create them
            #If they do compare hashes

            # for index in range(0, len(values)):
            #     #print(f"\n\n {values[index]} \n\n")
            #     print(f"\n {values[0]} \n")

            #Insert or Update odoo db with op data if old_hash = new_hash
            #Check if id exists in odoo if not insert if yes update
            