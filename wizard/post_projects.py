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


class PostProjects(models.TransientModel):
    _name = 'post.projects'
    _description = 'Create Projects'
    base_path = "http://localhost:3000"
    endpoint_url = "/api/v3/projects/"
    hashed_project = hashlib.sha256()
    hashed_op_project = hashlib.sha256()
    headers = {
        'content-type': 'application/json'
    }

    def get_payload(self,id):
        payload = {
            "identifier": "what%s"%(id),
            "name": "what%s"%(id),
                    "active": True,
                    "public": False,
                    "description": {
                        "format": "markdown",
                        "raw": None,
                        "html": ""
                    },
            "statusExplanation": {
                        "format": "markdown",
                        "raw": None,
                        "html": ""
                    },
            "_links": {
                        "parent": {
                            "href": None
                        },
                        "status": {
                            "href": None
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

    def cron_create_projects(self):

        main_url = "%s%s" % (self.base_path, self.endpoint_url)

        try:
            for id in range(0,1000):
                response = self.post_response(main_url, self.get_payload(id))
                print(response)
        except Exception as e:
            print("Exception has ocurred: ", e)
            print("Exception type: ", type(e))