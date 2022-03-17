from odoo import models
import requests
import json
import hashlib
import random


class UpdateTimeEntries(models.TransientModel):
    _name = 'update.time_entries'
    _description = 'Update Time Entries'
    base_path = "http://localhost:3000"
    endpoint_url = "/api/v3/time_entries/"
    hashed_project = hashlib.sha256()
    hashed_op_project = hashlib.sha256()
    headers = {
        'content-type': 'application/json'
    }

    @staticmethod
    def get_payload(project, work_package, activity):
        payload = {
            "comment": {
                "format": "plain",
                "raw": None,
                "html": ""
            },
            "spentOn": "2021-12-22",
            "hours": "PT1H",
            "_links": {
                "project": {
                    "href": "/api/v3/projects/%s" % project,
                },
                "workPackage": {
                    "href": "/api/v3/work_packages/%s" % work_package,
                },
                "activity": {
                    "href": "/api/v3/time_entries/activities/%s" % activity,
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

    def cron_update_time_entries(self):
        try:
            for id in range(1, 21):
                project = random.randint(1821, 1829)
                work_package = random.randint(34, 53)
                activity = random.randint(1, 4)
                main_url = "%s%s/%s" % (self.base_path, self.endpoint_url, id)
                response = self.patch_response(main_url, self.get_payload(project, work_package, activity))
        except Exception as e:
            print("Exception has occurred: ", e)
            print("Exception type: ", type(e))
