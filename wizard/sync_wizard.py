from odoo import models, fields, api

class SyncWizard(models.TransientModel):
    _name = 'sync.wizard'

    def btn_sync(self):
        
