from odoo import models, fields, api

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    jewellery_weight = fields.Float(string="Unit Weight (gm)")  
    purity = fields.Char(string="Purity")
    gold_waste = fields.Float(string='Gold Waste (%)')
    making_charge_per_gm = fields.Float(string='Making Charge per Gram')

    product_weight_gm = fields.Float(string="Product Weight (gm)")
    labour_charges = fields.Float(string="Labour Charges")

    @api.model
    def create(self, vals):
        # Step 1: Extract values
        quantity = vals.get('quantity', 0.0)
        price_unit = vals.get('price_unit', 0.0)
        discount = vals.get('discount', 0.0)

        # Step 2: Get product defaults
        if vals.get('product_id'):
            product = self.env['product.product'].browse(vals['product_id'])
            tmpl = product.product_tmpl_id

            vals.setdefault('jewellery_weight', tmpl.jewellery_weight or 0.0)
            vals.setdefault('gold_waste', tmpl.gold_waste or 0.0)
            vals.setdefault('making_charge_per_gm', tmpl.making_charge_per_gm or 0.0)
            vals.setdefault('purity', tmpl.jewellery_purity_id.name or "")

        # Step 3: Compute
        jewellery_weight = vals.get('jewellery_weight', 0.0)
        making_charge_per_gm = vals.get('making_charge_per_gm', 0.0)
        product_weight = quantity * jewellery_weight
        labour_charge = product_weight * making_charge_per_gm

        base_price = price_unit * quantity
        base_price -= base_price * (discount or 0.0) / 100.0

        subtotal = base_price + labour_charge

        # Step 4: Set manually
        vals['product_weight_gm'] = product_weight
        vals['labour_charges'] = labour_charge
        vals['price_subtotal'] = subtotal
        vals['price_total'] = subtotal  # Assuming no tax or inclusive tax handling

        # Step 5: Create line
        line = super().create(vals)

        # Step 6: Force recompute amount_untaxed on the parent move
        if line.move_id:
            line.move_id._compute_amount()

        return line
