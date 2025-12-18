from odoo import models, fields, api
from odoo.tools import file_open
from odoo.exceptions import ValidationError

import base64


class Employee(models.Model):
    _inherit = "hr.employee"
    _description = "Employee model"

    # == FIELDS == #

    is_workshop_employee = fields.Boolean(string="Workshop employee", default=False)
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
    employee_type = fields.Selection(
        selection_add=[
            ("mechanic", "Mechanic"),
            ("apprentice", "Apprentice"),
            ("administrative", "Administrative"),
            ("workshop_manager", "Workshop Manager"),
        ],
        ondelete={
            "mechanic": "cascade",
            "apprentice": "cascade",
            "administrative": "cascade",
            "workshop_manager": "cascade",
        },
        default="mechanic",
    )
    is_available = fields.Boolean(string="Available", default=True)
    maintenance_ids = fields.One2many(
        "workshop.maintenance", "mechanic_id", string="Mechanic's Maintenances"
    )

    # == HELPERS METHODS == #

    @api.model
    def _get_default_avatar(self):
        try:
            with file_open("workshop/static/src/img/user_default.png", "rb") as f:
                return base64.b64encode(f.read())
        except Exception:
            return False

    def _create_user_from_employee(self):
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

            partner = self.env["res.partner"].search(
                [("email", "=", self.email)], limit=1
            )
            if not partner:
                partner = self.env["res.partner"].create(
                    {
                        "name": self.name,
                        "email": self.email,
                        "type": "contact",
                        "is_company": False,
                    }
                )

            user_vals = {
                "name": self.name,
                "login": self.email,
                "email": self.email,
                "partner_id": partner.id,
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            self.env.ref("base.group_user").id,
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
            raise ValidationError("Could not create user: %s" % str(e))

    # == CRUD METHODS == #

    @api.model_create_multi
    def create(self, vals_list):
        employees = super().create(vals_list)
        for employee in employees:
            if employee.email:
                employee._create_user_from_employee()
        return employees
