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
from datetime import timedelta
import isodate
import json

#TODO
#Loop through every project
class SyncVersions(models.TransientModel):

    _name = 'sync.versions'
    _description = 'Synchronize Versions'
    base_path = "http://localhost:3000"
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
    
    def get_data_to_update(self,limit):
        now=datetime.now()
        comp_date = now - timedelta(minutes=2)
        projects=self.env['op.project'].search([['write_date','<',comp_date,]],limit=limit)
        return projects

    def get_hashed(self,_id,identifier,name,public):
        hashable=json.dumps(_id) + identifier + name + json.dumps(public)
        hashed=hashlib.md5(hashable.encode("utf-8")).hexdigest()
        return hashed

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
                    _name = v['name']
                    _description = v['description']['raw']
                    _status = v['status']
                    start_date = v['startDate']
                    end_date = v['endDate']
                    _project_href = v['_links']['definingProject']['href']
                    _project_id = self.get_project_id(_project_href)

                    hashable_op_ver = _id + _project_id + _name + _description + _status

                    # exists = self.env.cr.execute("""SELECT 1 FROM op_project_version WHERE id=%s"""%(_id))
                    versions=self.env['op.project.version'].search([['db_id','=',_id]])
                    if(versions.exists()):
                        ver_id = json.dumps(versions.db_id)
                        ver_project_id = json.dumps(versions.db_project_id)
                        ver_name = versions.name
                        ver_description = versions.description
                        ver_status = versions.status

                        hashable_ver = ver_id + ver_project_id + ver_name + ver_description + ver_status

                        hashed_ver = hashlib.md5(hashable_ver.encode("utf-8")).hexdigest()
                        hashed_op_ver = hashlib.md5(hashable_op_ver.encode("utf-8")).hexdigest()
                        print("version id: ", ver_id)
                        print(hashed_ver)
                        print(hashed_op_ver)
                        
                        if(hashed_ver!=hashed_op_ver):
                            try:
                                print("Updating version...\n")
                                vals = {
                                    'db_id':_id,
                                    'db_project_id':_project_id,
                                    'name':_name,
                                    'description':_description,
                                    'status':_status
                                }
                                versions.write(vals)
                            except Exception as e:
                                print("Exception has ocurred: ", e)
                                print("Exception type: ", type(e))
                        else:
                            print("Version up to date\n")
                    else:
                        try:
                            print("Creating version...\n")
                            vals = {
                                'db_id':_id,
                                'db_project_id':_project_id,
                                'name':_name,
                                'description':_description,
                                'status':_status
                            }
                            versions.create(vals)
                        except Exception as e:
                            print("Exception has ocurred: ", e)
                            print("Exception type: ", type(e))
            else:
                print("Permission denied to project %d" % (_id))