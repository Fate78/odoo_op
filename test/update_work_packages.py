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


class UpdateWorkPackages(models.TransientModel):
    _name = 'update.work_packages'
    _description = 'Update Work_Packages'
    hashed_project = hashlib.sha256()
    hashed_op_project = hashlib.sha256()
    headers = {
        'content-type': 'application/json'
    }

    def get_main_url(self,project_id):
            base_path = "http://localhost:3000"
            endpoint_url = "/api/v3/projects/%s/work_packages"%project_id
            main_url="%s%s" % (base_path, endpoint_url)
            return main_url

    def get_payload(self,project_id,id):
        payload = {
            "subject": "updated%s"%id,
            "description": {
                "format": "markdown",
                "raw": None,
                "html": ""
            },
            "scheduleManually": False,
            "startDate": None,
            "dueDate": None,
            "estimatedTime": None,
            "percentageDone": 0,
            "remainingTime": None,
            "_links": {
                "category": {
                    "href": None
                },
                "type": {
                    "href": "/api/v3/types/1",
                    "title": "Task"
                },
                "priority": {
                    "href": "/api/v3/priorities/8",
                    "title": "Normal"
                },
                "project": {
                    "href": "/api/v3/projects/%s"%project_id,
                    "title": "project1"
                },
                "status": {
                    "href": "/api/v3/statuses/1",
                    "title": "New"
                },
                "responsible": {
                    "href": None
                },
                "assignee": {
                    "href": None
                },
                "version": {
                    "href": None
                },
                "parent": {
                    "href": None,
                    "title": None
                }
            }
        }
        return payload

    def get_api_key(self):
        api_key = self.env['ir.config_parameter'].sudo(
        ).get_param('openproject.api_key') or False
        return api_key

    def patch_response(self, url, payload):
        api_key = self.get_api_key()

        resp = requests.patch(
            url,
            auth=('apikey', api_key),
            data=json.dumps(payload),
            headers=self.headers
        )
        return json.loads(resp.text)

    def cron_update_work_packages(self):
        try:
            for p in range(1821,1830):
                main_url = self.get_main_url(p)
                print(p)
                print("main_url: ",main_url)
                for id in range(1,5):
                    response = self.patch_response(main_url, self.get_payload(p,id))
                    print(response)
        except Exception as e:
            print("Exception has ocurred: ", e)
            print("Exception type: ", type(e))