from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    gold_rate_per_gm = fields.Float(string='Gold Rate (gm)')


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    jewellery_weight = fields.Float(string="Unit Weight (gm)")
    purity = fields.Char(string="Purity")
    gold_waste = fields.Float(string='Gold Waste (%)')
    making_charge_per_gm = fields.Float(string='Making Charge per Gram')

    product_weight_gm = fields.Float(string="Product Weight (gm)", compute="_compute_jewellery_totals", store=True)
    labour_charges = fields.Float(string="Labour Charges", compute="_compute_jewellery_totals", store=True)

    @api.onchange('product_id')
    def _onchange_product_id_jewellery_fields(self):
        if self.product_id:
            template = self.product_id.product_tmpl_id
            self.jewellery_weight = template.jewellery_weight
            self.gold_waste = template.gold_waste
            self.making_charge_per_gm = template.making_charge_per_gm
            self.purity = template.jewellery_purity_id.name if template.jewellery_purity_id else ""

    @api.depends('product_qty', 'jewellery_weight', 'making_charge_per_gm')
    def _compute_jewellery_totals(self):
        for line in self:
            line.product_weight_gm = line.product_qty * line.jewellery_weight
            line.labour_charges = line.product_weight_gm * line.making_charge_per_gm

    @api.depends('product_qty', 'price_unit', 'taxes_id', 'currency_id', 'labour_charges')
    def _compute_amount(self):
        for line in self:
            base_price = line.price_unit * line.product_qty
            subtotal = base_price + line.labour_charges

            # Recalculate taxes on base price only (if desired)
            taxes = line.taxes_id.compute_all(
                line.price_unit,
                line.order_id.currency_id,
                line.product_qty,
                product=line.product_id,
                partner=line.order_id.partner_id
            )
            tax_amount = taxes['total_included'] - taxes['total_excluded']

            # Update fields
            line.price_tax = tax_amount
            line.price_subtotal = subtotal  # Includes labour
            line.price_total = subtotal + tax_amount

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        for line in lines:
            if line.order_id:
                line.order_id._amount_all()  # Re-trigger parent total
        return lines

    def write(self, vals):
        result = super().write(vals)
        for line in self:
            if line.order_id:
                line.order_id._amount_all()
        return result
