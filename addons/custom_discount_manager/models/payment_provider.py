from odoo import models, fields, api


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    # === FIELDS === #

    product_id = fields.Many2one('product.product', string='Product')
    name = fields.Char(string="name")
    discount_type = fields.Selection(
        selection=[
            ('fixed', 'Fixed Amount'),
            ('percentage', 'Percentage Amount'),
        ],
        string="Amount Type",
        default='fixed',
        required=True
    )
    amount_fixed = fields.Float(string="Fixed Amount")
    amount_percentage = fields.Integer(string="Percentage Amount")

    # === METHODS === #

    @api.model_create_multi
    def create(self, vals_list):
        providers = super(PaymentProvider, self).create(vals_list)
        for provider in providers:
            if not provider.product_id:
                provider._create_discount_product()
        return providers

    def write(self, vals):
        res = super(PaymentProvider, self).write(vals)
        for provider in self:
            if not provider.product_id:
                provider._create_discount_product()
            else:
                provider.product_id.write({
                    'name': ('%s') % provider.name,
                    'type': 'service',
                    'taxes_id': False,
                    'list_price': 0,
                    'active': True,
                    'sale_ok': False,
                    'purchase_ok': False,
                })
        return res

    def _create_discount_product(self):
        product_obj = self.env['product.product']
        for record in self:
            discount = record.amount_fixed if record.amount_fixed != 0 else record.amount_percentage
            new_product = product_obj.create({
                'name': ('%s') % record.name,
                'type': 'service',
                'taxes_id': False,
                'list_price': 0,
                'active': True,
                'sale_ok': False,
                'purchase_ok': False,
            })
            record.product_id = new_product.id
