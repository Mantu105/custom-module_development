from odoo import http, fields
from odoo.http import request
from odoo.exceptions import AccessDenied
from odoo.addons.website.controllers.main import Website

class TenderBidController(http.Controller):

    @http.route('/tender/bid/<int:tender_id>', type='http', auth='public', website=True)
    def tender_bid_form(self, tender_id, vendor_id=None, **kwargs):
        tender = request.env['tender.tender'].sudo().browse(tender_id)
        vendor = request.env['res.partner'].sudo().browse(int(vendor_id)) if vendor_id else None

        existing_tender_bid = request.env['tender.bid'].sudo().search([('tender_id', '=', tender.id), ('vendor_id', '=', vendor.id)], limit=1) if tender and vendor else None

        if existing_tender_bid:
            return request.render("tender_management_system.tender_bid_already_submitted")

        if tender.tender_closing_date < fields.Date.today():
            return request.render("tender_management_system.tender_closed")

        return request.render("tender_management_system.tender_bid_form", {
            'tender': tender,
            'vendor': vendor,
        })

    @http.route('/tender/bid/submit', type='http', auth='public', methods=['POST'], website=True, csrf=False)
    def submit_tender_bid(self, **post):
        tender_id = int(post.get('tender_id'))
        vendor_id = int(post.get('vendor_id'))
        bid_lines = []

        tender = request.env['tender.tender'].sudo().browse(tender_id)
        vendor = request.env['res.partner'].sudo().browse(vendor_id)

        existing_bid = request.env['tender.bid'].sudo().search([('tender_id', '=', tender.id), ('vendor_id', '=', vendor.id)], limit=1) if tender and vendor else None
        if existing_bid:
            return request.render("tender_management_system.tender_bid_already_submitted")

        total_amount = 0.0
        for line in tender.line_ids:
            price_key = f'price_{line.id}'
            if price_key in post:
                try:
                    price = float(post[price_key])
                    total_amount += price * line.quantity
                    bid_lines.append((0, 0, {
                        'product_id': line.product_id.id,
                        'price': price,
                        'quantity': line.quantity,
                    }))
                except ValueError:
                    continue
        if tender.minimun_bid_amount > total_amount or tender.maximum_bid_amount < total_amount:
            state = 'disqualified'
        else:
            state = 'qualified'
        if bid_lines:
            request.env['tender.bid'].sudo().create({
                'tender_id': tender.id,
                'vendor_id': vendor.id,
                'line_bid_ids': bid_lines,
                'qualification_status': state
            })

        return request.render("tender_management_system.thank_you_page")
