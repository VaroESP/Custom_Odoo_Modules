from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.osv import expression
import logging

_logger = logging.getLogger(__name__)


class CustomShopFilter(WebsiteSale):

    def _get_search_options(self, category=None, attrib_values=None, pricelist=None, min_price=0.0, max_price=0.0, **post):
        options = super()._get_search_options(
            category=category,
            attrib_values=attrib_values,
            pricelist=pricelist,
            min_price=min_price,
            max_price=max_price,
            **post
        )
        
        range_attributes = request.env['product.attribute'].sudo().search([
            ('display_type', '=', 'range')
        ])

        for attr in range_attributes:
            attr_id = str(attr.id)
            current_min = post.get(f'current_min_{attr_id}') or request.httprequest.args.get(
                f'current_min_{attr_id}')
            current_max = post.get(f'current_max_{attr_id}') or request.httprequest.args.get(
                f'current_max_{attr_id}')

            if current_min and current_max:
                try:
                    c_min = int(current_min)
                    c_max = int(current_max)

                    if c_max >= c_min:
                        attribute_values = request.env['product.attribute.value'].sudo().search([
                            ('attribute_id', '=', attr.id),
                            ('is_range_value', '=', True),
                            ('minimum_value', '<=', c_max),
                            ('maximum_value', '>=', c_min),
                        ])

                        if attribute_values:
                            if 'attrib_values' not in options:
                                options['attrib_values'] = []

                            for val in attribute_values:
                                options['attrib_values'].append(
                                    (attr.id, val.id))
                        else:
                            if 'attrib_values' not in options:
                                options['attrib_values'] = []
                            options['attrib_values'].append((attr.id, -1))

                except ValueError:
                    continue
        return options

    @http.route(['/shop', '/shop/page/<int:page>'], type='http', auth="public", website=True)
    def shop(self, page=0, category=None, search='', **post):
        response = super().shop(page=page, category=category, search=search, **post)

        range_attributes = request.env['product.attribute'].sudo().search([
            ('display_type', '=', 'range')
        ])

        current_ranges = {}
        for attr in range_attributes:
            attr_id = str(attr.id)
            current_min = post.get(f'current_min_{attr_id}') or request.httprequest.args.get(
                f'current_min_{attr_id}')
            current_max = post.get(f'current_max_{attr_id}') or request.httprequest.args.get(
                f'current_max_{attr_id}')

            if current_min and current_max:
                try:
                    c_min = int(current_min)
                    c_max = int(current_max)

                    if c_max >= c_min:
                        current_ranges[attr_id] = {
                            'min': c_min,
                            'max': c_max,
                            'attribute_min': attr.minimum,
                            'attribute_max': attr.maximum,
                            'name': attr.name,
                        }
                except ValueError:
                    continue

        response.qcontext.update({
            'range_attributes': range_attributes,
            'current_ranges': current_ranges,
        })

        return response
