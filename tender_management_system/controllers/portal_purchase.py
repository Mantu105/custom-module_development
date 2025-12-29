from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError, MissingError, ValidationError

class TenderController(http.Controller):

    @http.route('/my/tender', type='http', auth='user', website=True)
    def my_tenders(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        domain = [('partner_id.user_ids', '=', request.env.user.login), '|', ('origin', 'ilike', 'LB'), ('origin', 'ilike', 'TB'), ('state', 'in', ('draft', 'sent'))]

        if date_begin:
            domain.append(('create_date', '>=', date_begin))
        if date_end:
            domain.append(('create_date', '<=', date_end))

        if sortby == 'date':
            order = 'create_date desc'
        elif sortby == 'priority':
            order = 'priority desc'
        else:
            order = 'create_date desc'

        Tender = request.env['purchase.order']
        domain_count = Tender.sudo().search_count(domain)
        tenders = Tender.sudo().search(domain, order=order, limit=10, offset=(page - 1) * 10)

        return request.render('tender_management_system.tender_tree_template', {
            'tenders': tenders,
            'page': page,
            'date_begin': date_begin,
            'date_end': date_end,
            'sortby': sortby,
            'domain_count': domain_count,
            'pager': request.website.pager(
                url='/my/tender',
                total=domain_count,
                page=page,
                step=10
            ),
            'csrf_token': request.csrf_token()
        })

    @http.route(['/my/tender/<int:tender_id>'], type='http', auth="public", website=True)
    def portal_order_page(self, tender_id, **kw):
        try:
            warranty_repair = request.env['purchase.order'].sudo().browse(tender_id)

            if not warranty_repair.exists():
                return request.redirect('/my')

            values = {
                'tender_order': warranty_repair,
            }

            return request.render('tender_management_system.tender_form_template', values)

        except (AccessError, MissingError):
            return request.redirect('/my')
