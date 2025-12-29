from odoo import models, fields

class MedicineExpiryReportWizard(models.TransientModel):
    _name = 'medicine.expiry.report.wizard'
    _description = 'Medicine Expiry Report Wizard'

    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)

    def get_expired_medicines(self):
        return self.env['product.product'].search([
            ('expiry_date', '>=', self.start_date),
            ('expiry_date', '<=', self.end_date),
        ])

    def get_qty_available(self, product):
        return product.qty_available 

    def action_print_report(self):
        return self.env.ref('pharmacy_management_erp.action_medicine_expiry_report_custom').report_action(self)
