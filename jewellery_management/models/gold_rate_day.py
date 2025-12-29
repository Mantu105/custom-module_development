from odoo import models, fields, api

class GoldRatePerDay(models.Model):
    _name = 'gold.rate.per.day'
    _description = 'Gold Rate Per Day'

    date = fields.Date(string='Date', required=True, default=fields.Date.context_today)
    rate = fields.Float(string='Gold Rate/Day', required=True)

    def action_update_price(self):
        """Update product prices based on gold rate and product weight."""
        for record in self:
            products = self.env['product.template'].search([('type', '=', 'product'), ('gold_weight', '>', 0)])
            for product in products:
                new_price = record.gold_rate_per_gram * product.gold_weight
                product.list_price = new_price