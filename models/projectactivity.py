from odoo import models, fields, api


class ProjectActivity(models.Model):
    _name = 'op.project.activity'
    _description = 'Project Activity'

    op_project_id = fields.Many2one('op.project', string='Project', required=True)
    op_user_id = fields.Many2one('op.user', string='User', required=True)
    op_activity_id = fields.Many2one('op.activity', string='Activity', required=True)
    default_rate = fields.Monetary(string='Default Rate', required=True, default=0.0)
    currency_id = fields.Many2one('res.currency', related='op_project_id.currency_id', store=True, readonly=True)