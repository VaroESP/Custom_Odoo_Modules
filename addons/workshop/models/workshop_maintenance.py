from odoo import models, fields, api
from odoo.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)


class Maintenance(models.Model):
    _name = "workshop.maintenance"
    _description = "Workshop Maintenance"
    _inherit = ["mail.thread", "mail.activity.mixin"]  # Agregado para seguimiento

    # == FIELDS == #

    name = fields.Char(string="Name", default="New")
    date_request = fields.Date(string="Date request")
    date_start = fields.Date(string="Date Start")
    date_end = fields.Date(string="Date end")
    date_delivery = fields.Date(string="Date delivery")
    kms = fields.Integer(string="Kilometers")
    customer_id = fields.Many2one(
        "res.partner",
        string="Customer",
        required=True,
        domain=[("is_workshop_customer", "=", True)],
        default=lambda self: self.env.user.partner_id.id,
    )
    vehicle_id = fields.Many2one("workshop.vehicle", string="Vehicle", required=True)
    product_ids = fields.Many2many(
        comodel_name="product.product",
        string="Products Used",
        domain="[('is_workshop_product', '=', True)]",
    )
    mechanic_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Mechanic",
        required=True,
        default=lambda self: (self.env.user.employee_id.id),
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("in_progress", "In progress"),
            ("quality_check", "Quality Check"),
            ("ready", "Ready for delivery"),
            ("delivered", "Delivered"),
            ("invoiced", "Invoiced"),
            ("cancelled", "Cancelled"),
        ],
        string="State",
        default="draft",
    )
    priority = fields.Selection(
        [("low", "Low"), ("normal", "Normal"), ("high", "High"), ("urgent", "Urgent")],
        string="Priority",
        default="normal",
    )
    problem_description = fields.Text(
        string="Problems description",
    )
    diagnosis = fields.Text(string="Diagnosis")
    internal_notes = fields.Text(string="Internal notes")
    customer_notes = fields.Text(string="Customer notes")
    line_ids = fields.One2many(
        "workshop.maintenance.line", "maintenance_id", string="Maintenance lines"
    )
    total_hours = fields.Float(
        string="Total hours", compute="_compute_totals", store=True
    )
    total_parts = fields.Monetary(
        string="Total spare parts", compute="_compute_totals", store=True
    )
    total_amount = fields.Monetary(
        string="Total amount", compute="_compute_totals", store=True
    )

    invoice_id = fields.Many2one("account.move", string="Invoice", readonly=True)
    invoiced_amount = fields.Monetary(
        string="Invoice amount",
        related="invoice_id.amount_total",
        currency_field="currency_id",
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
        required=True,
    )

    # == CRUD METHODS == #

    @api.model_create_multi
    def create(self, vals_list):

        for vals in vals_list:
            if vals.get("name", "New") == "New":

                # Get the customer_id and year
                base_code = "MNT"
                year = fields.Date.today().year

                # Get the base sequence
                seq_code = f"maintenance.order.{base_code}.{year}"

                # Search if the sequence exist
                sequence = self.env["ir.sequence"].search(
                    [("code", "=", seq_code)], limit=1
                )
                if not sequence:
                    sequence = self.env["ir.sequence"].create(
                        {
                            "name": f"Maintenance {base_code} {year}",
                            "code": seq_code,
                            "prefix": f"{base_code}/{year}/",
                            "padding": 4,
                            "number_increment": 1,
                            "implementation": "standard",
                            "use_date_range": False,
                        }
                    )

                vals["name"] = sequence.next_by_code(seq_code)

        return super(Maintenance, self).create(vals)

    @api.depends('line_ids.price_subtotal', 'line_ids.duration', 'line_ids.product_type')
    def _compute_totals(self):
        for record in self:
            service_lines = record.line_ids.filtered(
                lambda l: l.product_type == 'service'
            )
            record.total_hours = sum(service_lines.mapped('duration')) or 0.0
            
            parts_lines = record.line_ids.filtered(
                lambda l: l.product_type == 'consu'
            )
            record.total_parts = sum(parts_lines.mapped('price_subtotal')) or 0.0
            
            record.total_amount = sum(record.line_ids.mapped('price_subtotal')) or 0.0

    # == ONCHANGE METHODS == #
    
    @api.onchange('kms')
    def _onchange_kms(self):
        for record in self:
            if record.vehicle_id and record.kms:
                record.vehicle_id.write({
                    'kms': record.kms
                })
                
    # == ACTION METHODS == #

    def action_confirm(self):
        self.write({"state": "confirmed"})

    def action_start(self):
        self.write({"state": "in_progress", "date_start": fields.Date.today()})

    def action_complete(self):
        self.write({"state": "quality_check", "date_end": fields.Date.today()})

    def action_quality_approve(self):
        self.write({"state": "ready"})

    def action_delivery(self):
        self.write({"state": "delivered", "date_delivery": fields.Date.today()})

    def action_cancel(self):
        self.write({"state": "cancelled"})

    def action_create_invoice(self):
        """Generar PDF de factura"""
        self.write({'state': 'invoiced'})
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/report/pdf/workshop.workshop_maintenance_report_template/{self.id}',
            'target': 'new',
        }

    def action_print_invoice(self):
        """Alternativa para imprimir"""
        return self.action_create_invoice()