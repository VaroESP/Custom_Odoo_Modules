from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_payment_discount = fields.Boolean(
        string="Is payment discount", default=False)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # === FIELDS === #

    payment_method_id = fields.Many2one(
        'payment.method',
        string='Selected Payment Method'
    )
    payment_have_discount = fields.Boolean(
        compute='_compute_have_discount',
        default=False
    )
    discount = fields.Float(
        string="Discount", compute="_compute_have_discount", default=0)

    # === METHODS === #

    @api.depends('payment_method_id', 'discount')
    def _compute_have_discount(self):
        for order in self:
            pm_id = order.payment_method_id.id

            if not pm_id:
                order.payment_have_discount = False
                continue

            pm = self.env['payment.method'].sudo().browse(pm_id)
            _logger.info(f'varoESP: Sacamos el payment method: {pm}')
            provider = pm.provider_ids[:1]
            if provider:
                f_amount = provider.amount_fixed
                p_amount = provider.amount_percentage
                order.payment_have_discount = (f_amount > 0 or p_amount > 0)
                if f_amount != 0:
                    order.discount = -f_amount
                elif p_amount != 0:
                    lines_to_sum = self.order_line.filtered(
                        lambda l: not l.is_payment_discount)
                    subtotal = sum(lines_to_sum.mapped('price_subtotal'))
                    order.discount = - \
                        (subtotal * (provider.amount_percentage / 100.0))
            else:
                order.payment_have_discount = False

    def _update_payment_discount_line(self, payment_method_id):
        self.ensure_one()
        self.order_line.filtered(lambda l: l.is_payment_discount).unlink()

        if not payment_method_id:
            return

        pm = self.env['payment.method'].sudo().browse(payment_method_id)
        provider = pm.provider_ids[:1]

        if provider and (provider.amount_fixed > 0 or provider.amount_percentage > 0):
            if provider.discount_type == 'fixed':
                amount = -provider.amount_fixed
            else:
                subtotal = sum(self.order_line.mapped('price_subtotal'))
                amount = -(subtotal * (provider.amount_percentage / 100.0))

            self.env['sale.order.line'].sudo().create({
                'order_id': self.id,
                'product_id': provider.product_id.id,
                'price_unit': amount,
                'product_uom_qty': 1.0,
                'is_payment_discount': True,
                'sequence': 999,
            })
        self._compute_tax_totals()
