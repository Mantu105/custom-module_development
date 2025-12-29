from odoo import models, fields, api

class StockMove(models.Model):
    _inherit = 'stock.move'

    jewellery_weight = fields.Float(string="Weight (gm)")
    purity = fields.Char(string="Purity") 
    gold_waste = fields.Float(string='Gold Waste (%)')
    making_charge_per_gm = fields.Float(string='Making Charge per Gram')
    product_weight_gm = fields.Float(string="Product Weight (gm)")

    @api.model
    def create(self, vals):
        if vals.get('product_id'):
            product = self.env['product.product'].browse(vals['product_id'])
            tmpl = product.product_tmpl_id
            vals.setdefault('jewellery_weight', tmpl.jewellery_weight)
            vals.setdefault('gold_waste', tmpl.gold_waste)
            vals.setdefault('making_charge_per_gm', tmpl.making_charge_per_gm)
            vals.setdefault('purity', tmpl.jewellery_purity_id.name or "")


            # Calculate product weight = quantity * unit jewellery weight
            quantity = vals.get('product_uom_qty', 0.0)
            vals['product_weight_gm'] = quantity * tmpl.jewellery_weight
        return super().create(vals)
