from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Product(models.Model):
    _inherit = "product.template"
    _description = "Product model"

    # == FIELDS == #

    is_workshop_product = fields.Boolean(string="Workshop product", default=False)
    maintenance_ids = fields.Many2many(
        comodel_name="workshop.maintenance",
        string="Maintenances",
    )

    # == ACTION METHODS == #

    def action_view_maintenances(self):
        return {
            "name": "Maintenances using this product",
            "type": "ir.actions.act_window",
            "res_model": "workshop.maintenance",
            "view_mode": "tree,form",
            "domain": [("product_ids", "in", self.product_variant_ids.ids)],
            "context": {},
        }
