# -*- coding: utf-8 -*-
from odoo import models, fields
from datetime import datetime
from datetime import timedelta
import requests
import json


class OpenProjectBaseMethods(models.AbstractModel):
    _name = 'openproject.base_methods'
    _description = "Abstract Model for methods"

    base_path = "http://localhost:3000"
    filters = "?filters=[]&offset=1&pageSize=20"

    # Searches the database of a model for data that hasn't been updated in a certain time
    def get_data_to_update(self, model, limit):
        now = datetime.now()
        comp_date = now - timedelta(minutes=1)  # defines the interval of time of when to check
        data = self.env[model].search([['write_date', '<', comp_date, ]], limit=limit)
        return data

    # gets the api_key from param 'openproject.api_key' from 'ir.config_parameter' model
    def get_api_key(self):
        api_key = self.env['ir.config_parameter'].sudo().get_param('openproject.api_key') or False
        return api_key

    # requests the OP url with api_key and returns json data
    def get_response(self, url):
        api_key = self.get_api_key()

        resp = requests.get(
            url,
            auth=('apikey', api_key)
        )
        return json.loads(resp.text)

    # input url and payload and insert data into OP
    def post_response(self, url, payload):
        api_key = self.get_api_key()

        headers = {
            'content-type': 'application/json'
        }
        resp = requests.post(
            url,
            auth=('apikey', api_key),
            data=json.dumps(payload),
            headers=headers
        )
        return json.loads(resp.text)

    # get id through href
    @staticmethod
    def get_id_href(href):
        _id = href.split('/')[-1]
        return _id

    # input time string and return time float
    @staticmethod
    def get_time_float(time_str):
        h, m, s = time_str.split(':')
        return int(h) + int(m) / 60

    # Verify if field is False or None and initialize it
    @staticmethod
    def verify_field_empty(field):
        if not field:
            field = ""
        if field is None:
            field = ""
        return field

    def get_projects_url(self):
        base_path = self.base_path
        filters = self.filters
        endpoint_url = "/api/v3/projects/"
        main_url = "%s%s%s" % (base_path, endpoint_url, filters)
        return main_url

    def get_project_url(self, project_id):
        base_path = self.base_path
        filters = self.filters
        endpoint_url = "/api/v3/projects/%s" % project_id
        main_url = "%s%s%s" % (base_path, endpoint_url, filters)
        return main_url

    def check_next_offset(self, response):
        next_offset = False
        for r in response['_links']:
            if 'nextByOffset' in r:
                next_offset = True
                main_url = "%s%s" % (self.base_path, response['_links']['nextByOffset']['href'])
                response = self.get_response(main_url)
        return next_offset, response


"""Abstract class with methods inherited by all other classes"""


class OpenProjectBase(models.AbstractModel):
    _name = 'openproject.base'
    _description = "Abstract Model for other tables"
    _order = 'db_id desc'
    _inherit = ['openproject.base_methods']

    db_id = fields.Integer(
        'DB_ID', readonly=True, help="Stores the id from OP (OP_DB)", index=True, required=True)


"""Abstract class with fields that interact with the tables"""


class Project(models.Model):
    _name = 'op.project'
    _description = 'Project (OP)'
    _inherit = ['openproject.base']
    _order = 'db_id desc'

    # Real Odoo model records
    op_identifier = fields.Char(
        string="Identifier (OP)", readonly=True, required=True)
    name = fields.Char(string="Name", readonly=False,
                       required=True)
    public = fields.Boolean('Is Public', help='Is this a public project?', readonly=False, required=True)
    active = fields.Boolean('Is Active', help='Is this an active project?', readonly=False, required=True,
                            default=False)
    description = fields.Char(string="Description", readonly=False, required=False, default='')

    """TODO: Get these fields from OpenProject API"""
    partner_id = fields.Many2one('res.partner', string='Customer')
    billable = fields.Selection(
        [('no', 'No'), ('yes', 'Yes')], string='Billable', required=False, default='no')
    default_rate = fields.Monetary(
        string='Default Rate', required=False, default=0.0)
    responsible_id = fields.Many2one('op.user', string='Responsible')  # responsible_id is in workpackages
    currency_id = fields.Many2one('res.currency', string='Currency', required=False,
                                  default=lambda self: self.env.user.company_id.currency_id)


class User(models.Model):
    _name = 'op.user'
    _inherit = ['openproject.base']
    _description = 'User (OP)'

    # Real Odoo model records
    firstname = fields.Char(string="First Name", readonly=False, required=True)
    lastname = fields.Char(string="Last Name", readonly=False, required=True)
    login = fields.Char(string="Login", readonly=False, required=True)
    email = fields.Char(string="Email", readonly=False, required=True)
    admin = fields.Boolean('Is Admin', help='Is this user an admin?', readonly=False, required=True)

    # return the api url for the users
    def get_users_url(self):
        base_path = self.base_path
        filters = self.filters
        endpoint_url = "/api/v3/users/"
        main_url = "%s%s%s" % (base_path, endpoint_url, filters)
        return main_url


class Activity(models.Model):
    _name = 'op.activity'
    _inherit = ['openproject.base']
    _description = 'Activity (OP)'

    # Real Odoo model records
    name = fields.Char(string='Name', readonly=False, required=True)

    def get_activities_url(self, _id):
        base_path = self.base_path
        filters = self.filters
        endpoint_url = "/api/v3/time_entries/activities/%s" % _id
        main_url = "%s%s%s" % (base_path, endpoint_url, filters)
        return main_url


class WorkPackage(models.Model):
    _name = 'op.work.package'
    _inherit = ['openproject.base']
    _description = 'Work Package (OP)'

    # As in OP database is
    db_project_id = fields.Integer('Project (OP_DB)', readonly=True, help="Stores the id from OP", index=True,
                                   required=True)
    db_responsible_id = fields.Integer('Responsible (OP_DB)', readonly=True, help="Stores the id from OP",
                                       required=False)
    db_author_id = fields.Integer('Author (OP_DB)', readonly=True, help="Stores the id from OP", required=True)

    # Real Odoo model records
    name = fields.Char(string="Name", readonly=False, required=True)
    description = fields.Char(string="Description", readonly=False, required=False, default='')
    spent_time = fields.Float('Spent Time', readonly=False, required=True, default=0.0)

    def get_project_workpackages_url(self, project):
        base_path = self.base_path
        filters = self.filters
        endpoint_url = "/api/v3/projects/%s/work_packages" % project

        return "%s%s%s" % (base_path, endpoint_url, filters)

    def get_workpackages_url(self):
        base_path = self.base_path
        filters = self.filters
        endpoint_url = "/api/v3/work_packages"

        return "%s%s%s" % (base_path, endpoint_url, filters)

    @staticmethod
    def get_payload(project_id, responsible_id, subject, description, start_date):
        payload = {
            "subject": "%s" % subject,
            "description": {
                "format": "markdown",
                "raw": description,
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
                    "href": "/api/v3/users/%s" % responsible_id
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


class TimeEntries(models.Model):
    _name = 'op.time.entry'
    _inherit = ['openproject.base']
    _description = 'Time Entries'

    # As in OP database is
    db_project_id = fields.Integer('Project (OP_DB)', readonly=True, required=True, help="Stores the id from OP")
    db_user_id = fields.Integer('User (OP_DB)', readonly=True, required=True, help="Stores the id from OP")
    db_work_package_id = fields.Integer('WP (OP_DB)', readonly=True, required=True, help="Stores the id from OP")
    db_activity_id = fields.Integer('Activity (OP_DB)', readonly=True, required=False, help="Stores the id from OP")
    # Real Odoo model records
    comment = fields.Char(string="Comment", readonly=False, required=False, default='')
    op_hours = fields.Float('Hours', readonly=False, required=True)
    op_spent_on = fields.Date(string='Spent On', readonly=False, required=True)

    def get_time_entries_url(self):
        base_path = self.base_path
        filters = self.filters
        endpoint_url = "/api/v3/time_entries"

        return "%s%s%s" % (base_path, endpoint_url, filters)


class Versions(models.Model):
    _name = 'op.project.version'
    _inherit = ['openproject.base']
    _description = "Project Versions"

    db_project_id = fields.Integer('Project (OP_DB)', readonly=True, required=True, help="Stores the id from OP")

    name = fields.Char(string="Name", readonly=False, required=True)
    description = fields.Char(string="Description", readonly=False, required=False, default="")
    status = fields.Selection([('open', 'Open'), ('locked', 'Locked'), ('closed', 'Closed')], string='Status',
                              required=False, default='open')

    def get_project_versions_url(self, project):
        base_path = self.base_path
        filters = self.filters
        endpoint_url = "/api/v3/projects/%s/versions" % project

        return "%s%s%s" % (base_path, endpoint_url, filters)

    def get_versions_url(self):
        base_path = self.base_path
        filters = self.filters
        endpoint_url = "/api/v3/versions"

        return "%s%s%s" % (base_path, endpoint_url, filters)


class ScheduledTasks(models.Model):
    _name = 'op.scheduled.tasks'
    _description = "Scheduled Tasks"
    _inherit = ['openproject.base_methods']

    name = fields.Char(string="Name", readonly=False, required=True)
    description = fields.Char(string="Description", readonly=False, required=False, default="")
    interval = fields.Integer(string="Interval", required=True, default=1)
    frequency = fields.Selection([('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')],
                                 string='Frequency', required=False, default='daily')
    projects = fields.Many2one('op.project', string="Project")
    active = fields.Boolean('Is Active', help='Is this an active scheduled task?', readonly=False, required=True,
                            default=True)
    run_today = fields.Boolean('Run Today', help='Should the task run today?', readonly=False, required=True,
                               default=True)
    write_date_test = fields.Datetime(string='Write Date Test', readonly=False, required=True,
                                      default=fields.Datetime.now)
    """TODO:
        Add a Due_Date 
        Add Processed field to use _trigger"""

    def get_data(self, limit):
        now = datetime.now()
        comp_date = now - timedelta(minutes=1)  # defines the interval of time of when to check
        data = self.env['op.scheduled.tasks'].search([['write_date', '<', comp_date, ]], limit=limit)
        return data
