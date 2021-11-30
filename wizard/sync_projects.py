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
            #print(r['description'])
            project_id = r['id']
            project_identifier = r['identifier']
            project_name = r['name']
            archived = r['active']
            dt_createdAt = parser.parse(r['createdAt'])
            dt_updatedAt = parser.parse(r['updatedAt'])
            public = r['public']
            print(project_id, project_identifier, project_name, public)
            #Select data and hash it
            # self.env.cr.execute("SELECT op_identifier, name, public FROM op_project")
            # projects_dict = self.env.cr.dictfetchall()

            #Insert or Update odoo db with op data
            try:
                self.env.cr.execute("""SELECT * FROM op_project WHERE id=%s"""%(project_id))
                projects_dict = self.env.cr.fetchall()
                print(f"\n {projects_dict[0]} \n")
                #id=0,identifier=6,name=7,public=8
                # for index in range(0, len(values)):
                #     #print(f"\n\n {values[index]} \n\n")
                #     print(f"\n {values[0]} \n")
                self.env.cr.execute("""INSERT INTO op_project(id, op_identifier, name, public)
                                    VALUES (%s, %s, %s, %s)
                                    ON CONFLICT (id) DO UPDATE
                                    SET id=%s, op_identifier=%s, name=%s, public=%s
                                    WHERE op_project.id=%s
                                    RETURNING op_identifier""",
                                (project_id, project_identifier, project_name, public, project_id, project_identifier, project_name, public, project_id))
            except Exception as e:
                print("Exception has ocurred: ", e)
                print("Exception type: ", type(e))