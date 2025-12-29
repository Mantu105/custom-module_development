from odoo import fields, models
import json

class PaymentProvider(models.Model):
    _inherit = "payment.provider"

    code = fields.Selection(selection_add=[('moyasar', "Moyasar")], ondelete={'moyasar': 'set default'})
    moyasar_public_key = fields.Char("Moyasar Public Key")
    moyasar_secret_key = fields.Char("Moyasar Secret Key")
