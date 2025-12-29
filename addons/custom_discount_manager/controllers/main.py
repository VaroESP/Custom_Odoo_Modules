from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class CustomDiscountController(WebsiteSale):        
    @http.route('/shop/payment/update_discount', type='json', auth='public', website=True)
    def update_payment_discount(self, payment_method_id=None, **post):
        order = request.website.sale_get_order()
        if not order:
            return False

        pm_id = int(payment_method_id) if payment_method_id else False
        
        order.sudo().write({'payment_method_id': pm_id})
        order.sudo()._update_payment_discount_line(pm_id)
        order.sudo()._compute_have_discount()
        
        return request.env['ir.ui.view'].sudo()._render_template(
            "website_sale.total", {
                'website_sale_order': order,
            }
        )