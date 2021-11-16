from odoo import models, fields, api

class SyncWizard(models.TransientModel):
    _name = 'sync.wizard'

    def btn_sync(self):
            notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': ('Notice'),
                'message': 'This function has not been implemented yet',
                'type':'warning',  #types: success,warning,danger,info
                'sticky': False,  #True/False will display for few seconds if false
            }}
            return notification
