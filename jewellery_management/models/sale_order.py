from odoo import models, fields,api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    gold_rate_per_gm = fields.Float(string='Gold Rate (gm)')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'


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

    @api.depends('product_uom_qty', 'jewellery_weight', 'making_charge_per_gm')
    def _compute_jewellery_totals(self):
        for line in self:
            line.product_weight_gm = line.product_uom_qty * line.jewellery_weight
            line.labour_charges = line.product_weight_gm * line.making_charge_per_gm

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'labour_charges')
    def _compute_amount(self):
        """
        Override the subtotal to include labour_charges
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            subtotal_base = price * line.product_uom_qty
            subtotal = subtotal_base + line.labour_charges

            taxes = line.tax_id.compute_all(
                price,
                line.order_id.currency_id,
                line.product_uom_qty,
                product=line.product_id,
                partner=line.order_id.partner_shipping_id,
            )
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': subtotal + (taxes['total_included'] - taxes['total_excluded']),
                'price_subtotal': subtotal,
            })
    
    