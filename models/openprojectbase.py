# -*- coding: utf-8 -*-

from odoo import models, fields, api


class OpenProjectBase(models.AbstractModel):
    _name = 'openproject.base'
    _description = "Abstract Model for other tables"
    _order = 'db_id desc'

    db_id = fields.Integer(
        'ID', readonly=True, help="Stores the id from OP (OP_DB)", index=True, required=False) # Required should be true

    # @api.multi
    def get_last_id(self):
        db_ids = self.search([], limit=1, order="db_id desc")
        return db_ids and max([n['db_id'] for n in db_ids]) or 0


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
    public = fields.Boolean(
        'Is Public', help='Is this a public project?', readonly=False, required=True)
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
    name = fields.Char(string="Name", readonly=False, required=True)
    login = fields.Char(string="Login", readonly=False, required=True)
    email = fields.Char(string="Email", readonly=False, required=True)

class Activity(models.Model):
    _name = 'op.activity'
    _inherit = ['openproject.base']
    _description = 'Activity (OP)'

    # Real Odoo model records
    name = fields.Char(string='Name', readonly=False, required=True)

class WorkPackage(models.Model):
    _name = 'op.work.package'
    _inherit = ['openproject.base']
    _description = 'Work Package (OP)'

    #@api.multi
    def _compute_op_url(self):
        for wp in self:
            # TODO: OpenProject domain should be a system parameter
            if wp.op_project_id:
                wp.op_url = 'https://pm.odoogap.com/projects/%s/work_packages/%s' % (
                    wp.op_project_id.op_identifier, wp.db_id)

    # As in OP database is
    db_project_id = fields.Integer('Project (OP_DB)', readonly=True, help="Stores the id from OP", index=True,
                                   required=True, default=0)
    db_responsible_id = fields.Integer('Responsible (OP_DB)', readonly=True, help="Stores the id from OP",
                                       required=True, default=0)
    db_author_id = fields.Integer('Author (OP_DB)', readonly=True, help="Stores the id from OP", required=True, default=0)

    # Real Odoo model records
    name = fields.Char(string="Name", readonly=False, required=True)
    op_project_id = fields.Many2one('op.project', 'Project (OP)', readonly=False)
    op_responsible_id = fields.Many2one('op.user', string='Responsible', index=True, readonly=False)
    op_author_id = fields.Many2one('op.user', string='Author', index=True, readonly=False)
    op_url = fields.Char('URL (OP)', compute='_compute_op_url', readonly=False)

class TimeEntries(models.Model):
    _name = 'op.time.entry'
    _inherit = ['openproject.base']
    _description = 'Time Entries'


    # As in OP database is
    db_project_id = fields.Integer('Project (OP_DB)', readonly=True, required=True, help="Stores the id from OP", default=0)
    db_user_id = fields.Integer('User (OP_DB)', readonly=True, required=True, help="Stores the id from OP", default=0)
    db_work_package_id = fields.Integer('Ticket (OP_DB)', readonly=True, required=True, help="Stores the id from OP", default=0)
    db_activity_id = fields.Integer('Activity (OP_DB)', readonly=True, required=True, help="Stores the id from OP", default=0)

    # Real Odoo model records
    name = fields.Char(string="Comment", readonly=False, required=True)
    op_hours = fields.Float('Hours', readonly=False, required=True)
    op_spent_on = fields.Date(string='Spent On', readonly=False, required=True)

class Versions(models.Model):
    _name = 'op.project.version'
    _inherit = ['openproject.base']
    _description = "Project Versions"

    db_project_id = fields.Integer('Project (OP_DB)', readonly=True, required=True, help="Stores the id from OP", default=0)

    name = fields.Char(string="Name", readonly=False, required=True)
    description = fields.Char(string="Description", readonly=False, required=True,default="")
    status = fields.Selection([('open', 'Open'), ('locked', 'Locked'), ('closed', 'Closed')], string='Status', required=False, default='open')

