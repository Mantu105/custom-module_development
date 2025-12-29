from odoo import http
from odoo.http import request

class MoyasarController(http.Controller):

    @http.route('/get/moyasar/order', type='http', auth='public', website=True)
    def get_moyasar_order(self, **kwargs):
        print("get_moyasar_order called with kwargs:", kwargs)
        order = request.website.sale_get_order()
        tx_id = order.transaction_ids and order.transaction_ids[0].id or False
        if order and kwargs.get('status') == 'paid':
            order.sudo().action_confirm()
            if tx_id:
                request.env['payment.transaction'].sudo().browse(tx_id).write({
                    'state': 'done',
                })
            return request.redirect('/shop/confirmation')
        if tx_id:
            request.env['payment.transaction'].sudo().browse(tx_id).write({
                'state': 'cancel',
            })
        return request.redirect('/shop/confirmation')


