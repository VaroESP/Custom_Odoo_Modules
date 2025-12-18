from odoo import models, fields, api


class WorkshopMaintenanceLine(models.Model):
    _name = "workshop.maintenance.line"
    _description = "Maintenance Lines"

    maintenance_id = fields.Many2one(
        "workshop.maintenance", string="Maintenance", ondelete="cascade"
    )
    product_id = fields.Many2one(
        "product.product",
        string="Product",
        required=True,
        domain="[('is_workshop_product', '=', True)]",
    )
    name = fields.Char(string="Description", compute="_compute_name", store=True)
    quantity = fields.Float(string="Quantity", default=1.0)
    unit_price = fields.Float(string="Unit Price", compute="_compute_unit_price", store=True, readonly=False)
    price_subtotal = fields.Float(
        string="Subtotal", compute="_compute_subtotal", store=True
    )
    product_type = fields.Selection(
        related="product_id.type", string="Type", store=True
    )
    duration = fields.Float(
        string="Duration", help="For services, duration in hours", default=1.0
    )

    @api.depends('product_id', 'product_id.name')
    def _compute_name(self):
        for line in self:
            if line.product_id:
                line.name = line.product_id.name
            else:
                line.name = False

    @api.depends('product_id')
    def _compute_unit_price(self):
        for line in self:
            if line.product_id:
                line.unit_price = line.product_id.list_price
            else:
                line.unit_price = 0.0

    @api.depends('quantity', 'unit_price', 'duration', 'product_type')
    def _compute_subtotal(self):
        for line in self:
            if line.product_type == 'service':
                line.price_subtotal = (
                    (line.quantity or 0.0)
                    * (line.unit_price or 0.0)
                    * (line.duration or 1.0)
                )
            else:
                line.price_subtotal = (line.quantity or 0.0) * (line.unit_price or 0.0)

    @api.depends('product_id', 'product_type')
    def _compute_duration(self):
        for line in self:
            if line.product_type == 'service':
                if not line.duration or line.duration == 0:
                    line.duration = 1.0
            else:
                line.duration = 0.0

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self._compute_unit_price()
            self._compute_name()
            self._compute_duration()