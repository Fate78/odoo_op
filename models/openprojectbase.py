# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from datetime import timedelta
import requests
import json

class OpenProjectBase(models.AbstractModel):
    _name = 'openproject.base'
    _description = "Abstract Model for other tables"
    _order = 'db_id desc'

    db_id = fields.Integer(
        'DB_ID', readonly=True, help="Stores the id from OP (OP_DB)", index=True, required=True)

    # @api.multi
    def get_last_id(self):
        db_ids = self.search([], limit=1, order="db_id desc")
        return db_ids and max([n['db_id'] for n in db_ids]) or 0

    def get_data_to_update(self,model,limit):
        now=datetime.now()
        comp_date = now - timedelta(minutes=2)
        data=self.env[model].search([['write_date','<',comp_date,]],limit=limit)
        return data
    #settings functions
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

    def get_projects_url(self):
        base_path = "http://localhost:3000"
        endpoint_url = "/api/v3/projects/"
        main_url = "%s%s" % (base_path,endpoint_url)
        return main_url

    #get id through href
    def get_id_href(self,href):
        _id = href.split('/')[-1]
        return _id
    
    #convert string duration to float  
    def get_timeFloat(self,time_str):
        h, m, s = time_str.split(':')
        return int(h) + int(m) / 60
    
    #Verifications
    def verify_field_empty(self,field):
        if(field==False):
            field=""
        if(field==None):
            field=""     
        return field

class Project(models.Model):
    _name = 'op.project'
    _description = 'Project (OP)'
    _inherit = ['openproject.base']
    _order = 'db_id desc'

    # Real Odoo model records
    op_identifier = fields.Char(
        string="Identifier (OP)", readonly=True, required=True, default=0)
    name = fields.Char(string="Name", readonly=False,
                       required=True)
    public = fields.Boolean('Is Public', help='Is this a public project?', readonly=False, required=True)
    active = fields.Boolean('Is Active', help='Is this an active project?', readonly=False, required=True, default=False)
    description = fields.Char(string="Description", readonly=False, required=False, default='')
    partner_id = fields.Many2one('res.partner', string='Customer')
    billable = fields.Selection(
        [('no', 'No'), ('yes', 'Yes')], string='Billable', required=False, default='no')
    default_rate = fields.Monetary(
        string='Default Rate', required=False, default=0.0)
    responsible_id = fields.Many2one('op.user', string='Responsible')
    currency_id = fields.Many2one('res.currency', string='Currency', required=False,
                                  default=lambda self: self.env.user.company_id.currency_id)
    op_activity_ids = fields.One2many('op.project.activity', 'op_project_id', string='Activities')


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
    
    def get_users_url(self):
        base_path = "http://localhost:3000"
        endpoint_url = "/api/v3/users/"
        main_url = "%s%s" % (base_path,endpoint_url)
        return main_url

class Activity(models.Model):
    _name = 'op.activity'
    _inherit = ['openproject.base']
    _description = 'Activity (OP)'
    
    # Real Odoo model records
    name = fields.Char(string='Name', readonly=False, required=True)
    
    def get_activities_url(self,_id):
        base_path = "http://localhost:3000"
        endpoint_url = "/api/v3/time_entries/activities/%s"%_id
        main_url = "%s%s" % (base_path,endpoint_url)
        return main_url

class WorkPackage(models.Model):
    _name = 'op.work.package'
    _inherit = ['openproject.base']
    _description = 'Work Package (OP)'

    def get_project_workpackages_url(self,project):
        base_path = "http://localhost:3000"
        endpoint_url = "/api/v3/projects/%s/work_packages" % (project)

        return "%s%s" % (base_path,endpoint_url)

    # As in OP database is
    db_project_id = fields.Integer('Project (OP_DB)', readonly=True, help="Stores the id from OP", index=True,
                                   required=True, default=0)
    db_responsible_id = fields.Integer('Responsible (OP_DB)', readonly=True, help="Stores the id from OP",
                                       required=False)
    db_author_id = fields.Integer('Author (OP_DB)', readonly=True, help="Stores the id from OP", required=True)

    # Real Odoo model records
    name = fields.Char(string="Name", readonly=False, required=True)
    description = fields.Char(string="Description", readonly=False, required=False, default='')
    spent_time = fields.Float('Spent Time', readonly=False, required=True, default=0.0)
    op_responsible_id = fields.Many2one('op.user', string='Responsible', index=True, readonly=False, required=False)
    op_author_id = fields.Many2one('op.user', string='Author', index=True, readonly=False, required=False)
    #op_url = fields.Char('URL (OP)', compute='_compute_op_url', readonly=False, required=False)

class TimeEntries(models.Model):
    _name = 'op.time.entry'
    _inherit = ['openproject.base']
    _description = 'Time Entries'

    def get_time_entries_url(self):
        base_path = "http://localhost:3000"
        endpoint_url = "/api/v3/time_entries"

        return "%s%s" % (base_path,endpoint_url)

    # As in OP database is
    db_project_id = fields.Integer('Project (OP_DB)', readonly=True, required=True, help="Stores the id from OP", default=0)
    db_user_id = fields.Integer('User (OP_DB)', readonly=True, required=True, help="Stores the id from OP", default=0)
    db_work_package_id = fields.Integer('Ticket (OP_DB)', readonly=True, required=True, help="Stores the id from OP", default=0)
    db_activity_id = fields.Integer('Activity (OP_DB)', readonly=True, required=True, help="Stores the id from OP", default=0)

    # Real Odoo model records
    comment = fields.Char(string="Comment", readonly=False, required=False, default='')
    op_hours = fields.Float('Hours', readonly=False, required=True)
    op_spent_on = fields.Date(string='Spent On', readonly=False, required=True)

class Versions(models.Model):
    _name = 'op.project.version'
    _inherit = ['openproject.base']
    _description = "Project Versions"

    def get_project_versions_url(self,project):
        base_path = "http://localhost:3000"
        endpoint_url = "/api/v3/projects/%s/versions" % (project)

        return "%s%s" % (base_path,endpoint_url)

    db_project_id = fields.Integer('Project (OP_DB)', readonly=True, required=True, help="Stores the id from OP", default=0)

    name = fields.Char(string="Name", readonly=False, required=True)
    description = fields.Char(string="Description", readonly=False, required=False,default="")
    status = fields.Selection([('open', 'Open'), ('locked', 'Locked'), ('closed', 'Closed')], string='Status', required=False, default='open')

