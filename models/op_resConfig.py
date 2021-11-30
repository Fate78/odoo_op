from odoo import models, fields, api

class OpResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    api_key = fields.Char(string='op_api', config_parameter="openproject.api_key")

    def set_api_key(self):
        res = super(OpResConfigSettings, self).set_api_key()
        self.env['ir.config_parameter'].set_param('openproject.api_key', False)
        return res
        
    @api.model
    def get_api_key(self):
        res = super(OpResConfigSettings, self).get_api_key()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        api_keys = ICPSudo.get_param('openproject.api_key')
        res.update(
            api_key=api_keys
        )
        return res