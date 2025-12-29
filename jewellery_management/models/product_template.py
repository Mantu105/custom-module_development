from odoo import models, fields,api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    jewellery_purity_id = fields.Many2one('jewellery.purity', string='Purity')
    making_style_id = fields.Many2one('jewellery.making.style', string='Making Style')
    making_charge_per_gm = fields.Float(string='Making Charge per Gram',compute="_compute_making_charge_per_gm",store=True,readonly=True,)
    jewellery_weight = fields.Float(string='Weight (in gm)')
    gold_waste = fields.Float(string='Gold Waste (%)')


    @api.depends('making_style_id')
    def _compute_making_charge_per_gm(self):
        for rec in self:
            rec.making_charge_per_gm = rec.making_style_id.charge_per_gram if rec.making_style_id else 0.0
 