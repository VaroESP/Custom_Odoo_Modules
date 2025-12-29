from odoo import models, fields, api
from odoo.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"
    _description = "Product attribute value model"

    # === FIELDS === #

    minimum_value = fields.Integer(
        string="Minimum",
        compute="_compute_min_max_values",
        store=True
    )
    maximum_value = fields.Integer(
        string="Maximum",
        compute="_compute_min_max_values",
        store=True
    )
    is_range_value = fields.Boolean(
        string="Is Range Value",
        store=True,
        default=False
    )

    # === METHODS === #

    @api.depends('name', 'attribute_id.display_type')
    def _compute_min_max_values(self):
        for record in self:
            if record.attribute_id.display_type == 'range' and record.name:
                try:
                    parts = record.name.split('-')
                    if len(parts) == 2:
                        record.minimum_value = int(parts[0].strip())
                        record.maximum_value = int(parts[1].strip())
                        record.is_range_value = True
                    else:
                        record.minimum_value = 0
                        record.maximum_value = 0
                        record.is_range_value = False
                except (ValueError, IndexError):
                    record.minimum_value = 0
                    record.maximum_value = 0
                    record.is_range_value = False
            else:
                record.minimum_value = 0
                record.maximum_value = 0
                record.is_range_value = False

    @api.constrains('name')
    def _check_name_format(self):
        for record in self:
            if record.attribute_id.display_type == 'range' and record.name:
                if '-' not in record.name:
                    raise ValidationError(
                        "Range values must be in format 'min - max' (e.g., '1 - 10')"
                    )

                try:
                    parts = record.name.split('-')
                    if len(parts) != 2:
                        raise ValidationError(
                            "Invalid format. Use 'min - max' (e.g., '1 - 10')"
                        )

                    min_val = int(parts[0].strip())
                    max_val = int(parts[1].strip())

                    if max_val <= min_val:
                        raise ValidationError(
                            "Maximum value must be greater than minimum value"
                        )

                    attribute = record.attribute_id
                    if attribute.minimum is not False and min_val < attribute.minimum:
                        raise ValidationError(
                            f"Minimum value ({min_val}) cannot be less than "
                            f"attribute's minimum ({attribute.minimum})"
                        )

                    if attribute.maximum is not False and max_val > attribute.maximum:
                        raise ValidationError(
                            f"Maximum value ({max_val}) cannot be greater than "
                            f"attribute's maximum ({attribute.maximum})"
                        )

                except ValueError:
                    raise ValidationError(
                        "Values must be valid integers"
                    )
