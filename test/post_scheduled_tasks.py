from requests.models import HTTPBasicAuth
from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime


class PostWorkPackages(models.AbstractModel):
    _name = 'post.work_packages'
    _description = 'Create Work_Packages'
    headers = {
        'content-type': 'application/json'
    }

    def get_payload(self, project_id, wp_ref, subject, start_date, due_date):
        payload = {
            "subject": "%s%s" % (subject, wp_ref),
            "description": {
                "format": "markdown",
                "raw": None,
                "html": ""
            },
            "scheduleManually": False,
            "startDate": start_date,
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
                    "href": "/api/v3/projects/%s" % project_id,
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

    def cron_create_work_packages(self):
        env_wp = self.env['op.work.package']
        project_url = env_wp.get_projects_url()
        response = env_wp.get_response(project_url)

        wp_ref = datetime.now().strftime("%Y-%m-%d")
        start_date = datetime.now()
        due_date = datetime.now + 4
        subject = "autoTask"

        for r in response['_embedded']['elements']:
            _project_id = r['id']
            work_package_url = env_wp.get_project_workpackages_url(_project_id)

            response = self.post_response(work_package_url, env_wp.get_payload(_project_id, wp_ref, subject, start_date, due_date))
            
        """TODO:
            http://localhost:3000/api/v3/projects/1843
            1. get memberships href and go over each membership
            2. get principal->user id from href
            2.1 save the members in a dictionary?
            3. create task in project_id with those members 
            3.1 create task
            3.2 get url for task
            3.3 go over the task and add assignee(s) and responsible"""