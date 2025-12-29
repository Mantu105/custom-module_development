from odoo import api, fields, models, _
from odoo.exceptions import UserError

class TenderBid(models.Model):
    _name = 'tender.bid'
    _description = 'Tender Bid'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "id desc"

    name = fields.Char(
        string='Agreement', copy=False, readonly=True,
        default=lambda self: _('New'))
    tender_id = fields.Many2one('tender.tender', string='Tender', required=True, ondelete='cascade')
    vendor_id = fields.Many2one('res.partner', string='Vendor', required=True)
    bid_type = fields.Selection([
        ('line_bid', 'Line Bid'),
        ('total_bid', 'Total Bid')
    ], string='Bid Type', required=True, related='tender_id.bid_type')
    line_bid_ids = fields.One2many('tender.bid.line', 'tender_bid_id', string='Bid Lines')
    qualification_status = fields.Selection([
        ('draft', 'Draft'),
        ('qualified', 'Qualified'),
        ('disqualified', 'Disqualified')
    ], string='Qualification Status', default='draft')


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                seq = self.env['ir.sequence'].next_by_code('tender.bid')
                vals['name'] = seq or _('New')
        return super().create(vals_list)

class TenderBidLine(models.Model):
    _name = 'tender.bid.line'
    _description = 'Tender Bid Line'

    tender_bid_id = fields.Many2one('tender.bid', string='Tender Bid', required=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    quantity = fields.Float(string='Quantity', required=True)
    price = fields.Float(string='Price', required=True)