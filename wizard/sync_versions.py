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

#TODO
#Loop through every project
class SyncVersions(models.TransientModel):

    _name = 'sync.versions'
    _description = 'Synchronize Versions'
    base_path = "http://localhost:8080"
    endpoint_url = "/api/v3/projects/"
    hashed_ver = hashlib.sha256()
    hashed_op_ver = hashlib.sha256()

    def get_project_id(self,href):
        project_id = href.split('/')[-1]
        return project_id

    def get_project_versions_url(self,project):
        endpoint_url = "/api/v3/projects/%s/versions" % (project)

        return "%s" % (endpoint_url)

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

    def cron_sync_versions(self):

        #Loop through every project 
        projects_url = "%s%s" % (self.base_path, self.endpoint_url)
        response = self.get_response(projects_url)
        for r in response['_embedded']['elements']:
            _id = r['id']
            main_url = "%s%s" % (self.base_path,self.get_project_versions_url(_id))
            response_ver = self.get_response(main_url)
            print(main_url)
            if(response_ver['_type']!="Error"):
                for v in response_ver['_embedded']['elements']:
                    _id = json.dumps(v['id'])
                    name = v['name']
                    description = v['description']['raw']
                    status = v['status']
                    start_date = v['startDate']
                    end_date = v['endDate']
                    project_href = v['_links']['definingProject']['href']
                    project_id = self.get_project_id(project_href)

                    hashable_op_ver = _id + project_id + name + description + status

                    exists = self.env.cr.execute("""SELECT 1 FROM op_project_version WHERE id=%s"""%(_id))

                    if(self.env.cr.fetchone()!=None):
                        self.env.cr.execute("""SELECT * FROM op_project_version WHERE id=%s"""%(_id))
                        versions_dict = self.env.cr.fetchall()
                        ver_id = json.dumps(versions_dict[0][0])
                        ver_project_id = json.dumps(versions_dict[0][2])
                        ver_name = versions_dict[0][3]
                        ver_description = versions_dict[0][4]
                        ver_status = versions_dict[0][5]

                        hashable_ver = ver_id + ver_project_id + ver_name + ver_description + ver_status

                        hashed_ver = hashlib.md5(hashable_ver.encode("utf-8")).hexdigest()
                        hashed_op_ver = hashlib.md5(hashable_op_ver.encode("utf-8")).hexdigest()
                        print("version id: ", ver_id)
                        print(hashed_ver)
                        print(hashed_op_ver)
                        
                        if(hashed_ver!=hashed_op_ver):
                            try:
                                print("Updating version...\n")
                                self.env.cr.execute("""UPDATE op_project_version
                                                    SET db_project_id=%s, name=%s, description=%s, status=%s
                                                    WHERE op_project_version.id=%s
                                                    RETURNING name""",
                                                    (project_id, name, description, status, _id))
                            except Exception as e:
                                print("Exception has ocurred: ", e)
                                print("Exception type: ", type(e))
                        else:
                            print("Version up to date\n")
                    else:
                        try:
                            print("Creating version...\n")
                            self.env.cr.execute("""INSERT INTO op_project_version(id, db_project_id, name, description, status)
                                                VALUES (%s, %s, %s, %s, %s)
                                                RETURNING name""",
                                            (_id, project_id, name, description, status))
                        except Exception as e:
                            print("Exception has ocurred: ", e)
                            print("Exception type: ", type(e))
            else:
                print("Permission denied to project %d" % (_id))