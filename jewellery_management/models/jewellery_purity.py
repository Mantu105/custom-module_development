from odoo import models, fields

class JewelleryPurity(models.Model):
    _name = 'jewellery.purity'
    _description = 'Jewellery Purity'

    name = fields.Char(string='Purity Level', required=True)
