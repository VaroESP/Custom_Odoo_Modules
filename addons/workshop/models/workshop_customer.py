from odoo import models, fields, api
from odoo.tools import file_open
from odoo.exceptions import ValidationError

import base64


class Customer(models.Model):
    _inherit = "res.partner"
    _description = "Customer model"

    # == FIELDS == #

    is_workshop_customer = fields.Boolean(string="Workshop customer", default=False)
    vat = fields.Char(string="VAT")
    customer_type = fields.Selection(
        [("individual", "Individual"), ("company", "Company")],
        string="Customer Type",
        default="individual",
    )
    street = fields.Char(string="Street")
    postal_code = fields.Char(string="Postal Code")
    city = fields.Char(string="City")
    state_id = fields.Many2one(
        "res.country.state",
        string="State",
        ondelete="restrict",
        domain="[('country_id', '=?', country_id)]",
        store=True,
    )
    country_id = fields.Many2one(
        "res.country", string="Country", ondelete="restrict", store=True
    )
    avatar_128 = fields.Image(
        string="Avatar 128",
        max_width=128,
        max_height=128,
        store=True,
        default=lambda self: self._get_default_avatar(),
    )
    user_id = fields.Many2one("res.users", string="User ID")
    vehicle_ids = fields.One2many(
        "workshop.vehicle", "customer_id", string="Customer's Vehicles"
    )
    maintenance_ids = fields.One2many(
        "workshop.maintenance", "customer_id", string="Customer's Maintenances"
    )
    vehicle_count = fields.Integer(string="Vehicles", compute="_compute_count")
    maintenance_count = fields.Integer(string="Maintenances", compute="_compute_count")

    # == COMPUTED METHODS == #

    @api.depends("vehicle_ids", "maintenance_ids")
    def _compute_count(self):
        for record in self:
            record.vehicle_count = len(record.vehicle_ids)
            record.maintenance_count = len(record.maintenance_ids)

    # == HELPERS METHODS == #

    @api.model
    def _get_default_avatar(self):
        try:
            with file_open("workshop/static/src/img/user_default.png", "rb") as f:
                return base64.b64encode(f.read())
        except Exception:
            return False

    def _create_user_from_customer(self):
        self.ensure_one()
        if self.user_id:
            return self.user_id

        if not self.email:
            return False

        try:
            existing_user = self.env["res.users"].search(
                [("login", "=", self.email)], limit=1
            )

            if existing_user:
                self.user_id = existing_user.id
                return existing_user

            user_vals = {
                "name": self.name,
                "login": self.email,
                "email": self.email,
                "partner_id": self.id,
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            self.env.ref("base.group_portal").id,
                        ],
                    )
                ],
                "active": True,
                "company_id": self.env.company.id,
                "company_ids": [(6, 0, [self.env.company.id])],
            }

            user = (
                self.env["res.users"]
                .with_context(no_reset_password=False)
                .create(user_vals)
            )

            self.user_id = user.id
            return user

        except Exception as e:
            raise ValidationError("Error creating user: %s" % str(e))

    # == ACTION METHODS == #

    def action_vehicle(self):
        return {
            "name": "Vehicles",
            "type": "ir.actions.act_window",
            "res_model": "workshop.vehicle",
            "view_mode": "list,form",
            "domain": [("customer_id", "=", self.id)],
            "target": "current",
        }

    def action_maintenance(self):
        return {
            "name": "Maintenances",
            "type": "ir.actions.act_window",
            "res_model": "workshop.maintenance",
            "view_mode": "list,form",
            "domain": [("customer_id", "=", self.id)],
            "target": "current",
        }

    # == CRUD METHODS == #

    @api.model_create_multi
    def create(self, vals_list):
        customers = super().create(vals_list)
        for customer in customers:
            if customer.email:
                customer._create_user_from_customer()
        return customers
