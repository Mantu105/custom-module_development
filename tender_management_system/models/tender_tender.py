from odoo import api, fields, models, _
from odoo.exceptions import UserError

class TenderTender(models.Model):
    _name = 'tender.tender'
    _description = 'Tender Tender'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "id desc"

    name = fields.Char(
        string='Agreement', copy=False, readonly=True, required=True,
        default=lambda self: _('New'))
    active = fields.Boolean('Active', default=True)
    vendor_id = fields.Many2many('res.partner', string='Vendor', required=True)
    user_id = fields.Many2one('res.users', string='Buyer', required=True, default=lambda self: self.env.user.id)
    tender_closing_date = fields.Date(string='Tender Closing Date', required=True)
    bid_type = fields.Selection([
        ('line_bid', 'Line Bid'),
        ('total_bid', 'Total Bid')
    ], string='Bid Type', required=True, default='total_bid')
    minimun_bid_amount = fields.Float(string='Minimum Bid Amount', required=True)
    maximum_bid_amount = fields.Float(string='Maximum Bid Amount', required=True)
    rfq_created = fields.Boolean(string='RFQ Created', default=False)
    line_ids = fields.One2many('tender.line', 'tender_id', string='Tender Lines')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft')
    total_bid_count = fields.Integer(string='Total Bids', compute='_compute_total_bid_count')
    rfq_count = fields.Integer(string='Purchase', compute='_compute_rfq_count')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            closing_date = vals.get('tender_closing_date')
            closing_date = fields.Date.from_string(closing_date)
            if closing_date and closing_date < fields.Date.today():
                raise UserError(_("Tender Closing Date cannot be in the past."))
            if vals.get('name', _('New')) == _('New'):
                if vals.get('bid_type') == 'line_bid':
                    seq = self.env['ir.sequence'].next_by_code('tender.tender.line')
                    vals['name'] = seq or _('New')
                elif vals.get('bid_type') == 'total_bid':
                    seq = self.env['ir.sequence'].next_by_code('tender.tender.total')
                    vals['name'] = seq or _('New')
                else:
                    vals['name'] = self.env['ir.sequence'].next_by_code('tender.tender') or _('New')
        return super().create(vals_list)
    

    def write(self, vals):
        tenders_to_rename = self.env['tender.tender']
        if 'bid_type' in vals:
            tenders_to_rename = self.filtered(lambda t:
                t.bid_type != vals.get('bid_type', t.bid_type))

        res = super().write(vals)

        for tender in tenders_to_rename:
            if tender.bid_type == 'line_bid':
                code = 'tender.tender.line'
            elif tender.bid_type == 'total_bid':
                code = 'tender.tender.total'
            else:
                code = 'tender.tender'

            tender.name = self.env['ir.sequence'].next_by_code(code)

        return res
    

    def _compute_total_bid_count(self):
        for tender in self:
            tender.total_bid_count = self.env['tender.bid'].search_count([('tender_id', '=', tender.id)])

    def _compute_rfq_count(self):
        for tender in self:
            tender.rfq_count = self.env['purchase.order'].search_count([('origin', '=', tender.name)])

    def action_open(self):
        if not self.line_ids:
            raise UserError(_(f"You cannot open tender {self.name} because it does not contain any product lines."))

        for line in self.line_ids:
            if line.quantity <= 0:
                raise UserError(_("Quantity in tender lines must be greater than zero."))

        if self.minimun_bid_amount <= 0:
            raise UserError(_("Minimum Bid Amounts must be greater than zero."))

        if self.maximum_bid_amount <= self.minimun_bid_amount:
            raise UserError(_("Maximum Bid Ants must be greater than minimum bid amount."))

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for vendor in self.vendor_id:
            if not vendor.email:
                continue

            tender_link = f"{base_url}/tender/bid/{self.id}?vendor_id={vendor.id}"
            subject = _("Invitation to Tender %s") % self.name
            body = _(
                "Dear %s,<br/><br/>"
                "You are invited to submit your bid for tender <b>%s</b>.<br/>"
                "Please click the link below to access the bid form:<br/>"
                "<a href='%s'>Submit Your Bid</a><br/><br/>"
                "Closing Date: %s<br/><br/>"
                "Best regards,<br/>%s"
            ) % (
                vendor.name,
                self.name,
                tender_link,
                self.tender_closing_date,
                self.user_id.name,
            )

            mail_values = {
                'subject': subject,
                'body_html': body,
                'email_to': vendor.email,
                'email_from': self.env.user.email_formatted,
            }
            self.env['mail.mail'].sudo().create(mail_values).send()

        self.state = 'open'
        return True

    def action_cancel(self):
        self.state = 'cancelled'

    def action_tender_bid(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _("Tender Bid"),
            'res_model': 'tender.bid',
            'view_mode': 'list,form',
            'domain': [
                ('tender_id', '=', self.id)
            ],
            'target': 'current'
        }

    def action_rfq(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _("Purchase Orders"),
            'res_model': 'purchase.order',
            'view_mode': 'list,form',
            'domain': [
                ('origin', '=', self.name)
            ],
            'target': 'current'
        }

    def _tender_close_and_evaluation(self):
        """ Cron job to tenders closed and bids evaluation """
        today = fields.Date.today()
        expired_tenders = self.search([
            ('tender_closing_date', '<', today),
            ('state', '=', 'open')
        ])
        for tender in expired_tenders:
            tender.state = 'closed'

        tenders = self.search([('state', '=', 'closed'), ('rfq_created', '=', False)])
        for tender in tenders:
            tender._tender_bid_evaluate()

    def _tender_bid_evaluate(self):
        """ Close the tender and evaluate vendor bids if bid_type = total_bid """
        qualified_bids = self.env['tender.bid'].search([
            ('tender_id', '=', self.id),
            ('qualification_status', '=', 'qualified')
        ])

        if not qualified_bids:
            return

        if self.bid_type == 'total_bid':

            vendor_totals = {}
            for bid in qualified_bids:
                total_amount = sum(line.price * line.quantity for line in bid.line_bid_ids)
                vendor_totals[bid.id] = total_amount

            cheapest_bid_id = min(vendor_totals, key=vendor_totals.get)
            cheapest_bid = self.env['tender.bid'].browse(cheapest_bid_id)

            # Create RFQ (Purchase Order)
            self.env['purchase.order'].create({
                'partner_id': cheapest_bid.vendor_id.id,
                'origin': self.name,
                'order_line': [(0, 0, {
                    'product_id': line.product_id.id,
                    'product_qty': line.quantity,
                    'price_unit': line.price,
                }) for line in cheapest_bid.line_bid_ids]
            })

        elif self.bid_type == 'line_bid':

            cheapest_lines = {}

            for bid in qualified_bids:
                for line in bid.line_bid_ids:
                    product_id = line.product_id.id
                    line_total = line.price * line.quantity

                    if product_id not in cheapest_lines or line_total < (cheapest_lines[product_id][0].price * cheapest_lines[product_id][0].quantity):
                        cheapest_lines[product_id] = (line, bid)

            # Group lines vendor-wise for creating multiple RFQs
            vendor_lines_map = {}
            for product_id, (line, bid) in cheapest_lines.items():
                vendor_id = bid.vendor_id.id
                if vendor_id not in vendor_lines_map:
                    vendor_lines_map[vendor_id] = []
                vendor_lines_map[vendor_id].append((0, 0, {
                    'product_id': line.product_id.id,
                    'product_qty': line.quantity,
                    'price_unit': line.price,
                }))

            # Create RFQ per vendor
            for vendor_id, order_lines in vendor_lines_map.items():
                self.env['purchase.order'].create({
                    'partner_id': vendor_id,
                    'origin': self.name,
                    'order_line': order_lines
                })

        self.rfq_created = True

class TenderLine(models.Model):
    _name = 'tender.line'
    _description = 'Tender Line'

    tender_id = fields.Many2one('tender.tender', string='Tender', required=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    quantity = fields.Float(string='Quantity', required=True)