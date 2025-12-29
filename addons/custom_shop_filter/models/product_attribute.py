from odoo import models, fields, api, http
from odoo.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)


class ProductAttribute(models.Model):
    _inherit = 'product.attribute'
    _description = "Product attribute model"

    # === FIELDS === #

    minimum = fields.Integer(string="Minimum")
    maximum = fields.Integer(string="Maximum")

    display_type = fields.Selection(
        selection_add=[('range', 'Range')],
        string="Display Type",
        ondelete={'range': 'cascade'}
    )

    # === METHODS === #

    @api.constrains('minimum', 'maximum')
    def _check_attribute_range(self):
        for record in self:
            if record.display_type == 'range':
                if record.minimum is not False and record.maximum is not False:
                    if record.maximum <= record.minimum:
                        raise ValidationError(
                            "Maximum must be greater than minimum"
                        )
                    if record.minimum <= 0:
                        raise ValidationError(
                            "Minimum must be greater than zero"
                        )

    '''@api.onchange('display_type')
    def _onchange_display_type(self):
        if self.display_type != 'range':
            self.minimum = 0
            self.maximum = 0'''

    '''def get_range_values(self):
        self.ensure_one()
        minimum = self.minimum or 1
        maximum = self.maximum or 10
        return {
            'minimum': minimum,
            'maximum': maximum,
        }'''
