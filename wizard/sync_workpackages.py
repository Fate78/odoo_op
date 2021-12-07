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

class SyncWorkPackages(models.TransientModel):

    _name = 'sync.workpackages'
    _description = 'Synchronize Work Packages'
    base_path = "http://localhost:8080"
    endpoint_url = "/api/v3/projects/"
    hashed_wp = hashlib.sha256()
    hashed_op_wp = hashlib.sha256()

    #function to convert string duration to int
    def get_spentTime(self,time_str):
        h, m, s = time_str.split(':')
        return int(h) + int(m) / 60

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

    def get_project_id(self,href):
        project_id = href.split('/')[-1]
        return project_id

    def get_project_workpackages_url(self,project):
        endpoint_url = "/api/v3/projects/%s/work_packages" % (project)

        return "%s" % (endpoint_url)

    def cron_sync_workpackages(self):
        #Loop through every project
        projects_url = "%s%s" % (self.base_path, self.endpoint_url)
        response = self.get_response(projects_url)

        for r in response ['_embedded']['elements']:
            _id = r['id']
            active = r['active']
            if(active!=False):
                main_url = "%s%s" % (self.base_path,self.get_project_workpackages_url(_id))
                response_wp = self.get_response(main_url)
                for w in response_wp['_embedded']['elements']:
                    wp_id = w['id']
                    print(main_url)
                    spentTime = isodate.parse_duration(w['spentTime'])
                    string_spentTime = str(spentTime)
                    int_spentTime = self.get_spentTime(string_spentTime)
                    string_wp_id = json.dumps(wp_id)
                    hashable_op_wp = string_wp_id + string_spentTime

                    exists = self.env.cr.execute("""SELECT 1 FROM op_work_package WHERE id=%s"""%(wp_id))
                    
                    #If exists
                    if(self.env.cr.fetchone()!=None):
                        self.env.cr.execute("""SELECT * FROM op_work_package WHERE id=%s"""%(wp_id))
                        workpackages_dict = self.env.cr.fetchall()
                        string_id = json.dumps(workpackages_dict[0][0])
                        string_public = json.dumps(workpackages_dict[0][8])
                        name = workpackages_dict[0][5]
                        
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
            else:
                print("Permission denied to project %s" % (_id))