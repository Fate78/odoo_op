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


class PostTimeEntries(models.TransientModel):
    _name = 'post.time_entries'
    _description = 'Create Entries'
    base_path = "http://localhost:3000"
    endpoint_url = "/api/v3/time_entries/"
    hashed_project = hashlib.sha256()
    hashed_op_project = hashlib.sha256()
    headers = {
        'content-type': 'application/json'
    }

    def get_payload(self,id):
        payload = {
            "comment": {
                "format": "plain",
                "raw": None,
                "html": ""
            },
            "spentOn": "21-12-21",
            "hours": 1.5,
            "_links": {
                "project": {
                    "href": None
                },
                "workPackage": {
                    "href": None
                },
                "activity": {
                    "href": "/api/v3/time_entries/activities/1",
                    "title": "Management"
                }
            }
        }
        return payload

    def get_api_key(self):
        api_key = self.env['ir.config_parameter'].sudo(
        ).get_param('openproject.api_key') or False
        return api_key

    def post_response(self, url, payload):
        api_key = self.get_api_key()

        resp = requests.post(
            url,
            auth=('apikey', api_key),
            data=json.dumps(payload),
            headers=self.headers
        )
        return json.loads(resp.text)

    def cron_create_time_entries(self):

        main_url = "%s%s" % (self.base_path, self.endpoint_url)
        try:
            for id in range(1,10):
                response = self.post_response(main_url, self.get_payload(id))
                print(response)
        except Exception as e:
            print("Exception has ocurred: ", e)
            print("Exception type: ", type(e))