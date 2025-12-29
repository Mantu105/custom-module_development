# models/making_style.py

from odoo import models, fields

class MakingStyle(models.Model):
    _name = 'jewellery.making.style'
    _description = 'Jewellery Making Style'

    name = fields.Char(string='Making Style', required=True)
    charge_per_gram = fields.Float(string='Making Charge per(gm)', required=True)
