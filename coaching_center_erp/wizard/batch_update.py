from odoo import models, fields, api

class BatchUpdateWizard(models.TransientModel):
    _name = 'batch.update.wizard'
    _description = 'Batch Update Wizard'

    name = fields.Char(string='Batch Name', required=True, help="e.g. 'Morning 9-11'")

    def apply_update_batch(self):
        active_ids = self.env.context.get('active_ids')
        if active_ids:
            batches = self.env['coaching.batch'].browse(active_ids)
            for batch in batches:
                batch.name = self.name
        return {'type': 'ir.actions.act_window_close'}
