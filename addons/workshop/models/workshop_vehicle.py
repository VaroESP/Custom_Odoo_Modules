from odoo import models, fields, api
from odoo.tools import file_open
from dateutil.relativedelta import relativedelta

import base64


class Vehicle(models.Model):
    _name = "workshop.vehicle"
    _description = "Vehicle model"

    # == FIELDS == #

    name = fields.Char(string="Vehicle", compute="_compute_name_vehicle", store=True)
    plate = fields.Char(string="Plate", required=True)
    brand = fields.Char(string="Brand", required=True)
    model = fields.Char(string="Model", required=True)
    customer_id = fields.Many2one(
        "res.partner", string="Customer", domain=[("is_workshop_customer", "=", True)]
    )
    last_maintenance = fields.Date(
        string="Last maintenance", compute="_compute_last_maintenance", store=True
    )
    next_maintenance = fields.Date(
        string="Next maintenance", compute="_compute_next_maintenance", store=True
    )
    vehicle_category = fields.Selection(
        [
            ("car", "Car"),
            ("motorcycle", "Motorcycle"),
            ("truck", "Truck"),
            ("other", "Other"),
        ],
        default="car",
        string="Vehicle type",
        required=True,
    )
    kms = fields.Integer(string="Kilometers")
    maintenance_ids = fields.One2many(
        "workshop.maintenance", "vehicle_id", string="Vehicle's maintenances"
    )
    avatar_128 = fields.Image(
        string="avatar 128",
        max_width=128,
        max_height=128,
        store=True,
        default=lambda self: self._get_default_avatar(),
    )
    maintenance_count = fields.Integer(string="Maintenances", compute="_compute_count")
    notes = fields.Text(string="Notes")

    # == COMPUTED METHODS == #

    @api.depends("brand", "model")
    def _compute_name_vehicle(self):
        for record in self:
            if record.brand and record.model:
                brand_upper = str(record.brand or "").upper()
                model_upper = str(record.model or "").upper()
                parts = [brand_upper, model_upper]
                record.name = " ".join(filter(None, parts)) or False
            else:
                record.name = False

    @api.depends("maintenance_ids.date_end")
    def _compute_last_maintenance(self):
        for record in self:
            if record.maintenance_ids:
                last_maintenance = record.maintenance_ids.filtered(
                    lambda m: m.date_end
                ).sorted(key=lambda m: m.date_end, reverse=True)

                if last_maintenance:
                    record.last_maintenance = last_maintenance[0].date_end
                else:
                    record.last_maintenance = False
            else:
                record.last_maintenance = False

    @api.depends("last_maintenance")
    def _compute_next_maintenance(self):
        for record in self:
            if record.last_maintenance:
                record.next_maintenance = record.last_maintenance + relativedelta(
                    years=1
                )

    @api.depends("maintenance_ids")
    def _compute_count(self):
        for record in self:
            record.maintenance_count = len(record.maintenance_ids)

    # == HELPERS METHODS == #

    @api.model
    def _get_default_avatar(self):
        try:
            with file_open("workshop/static/src/img/car_default.png", "rb") as f:
                return base64.b64encode(f.read())
        except Exception:
            return False

    # == ACTION METHODS == #

    def action_maintenance(self):
        return {
            "name": "Maintenances",
            "type": "ir.actions.act_window",
            "res_model": "workshop.maintenance",
            "view_mode": "list,form",
            "domain": [("vehicle_id", "=", self.id)],
            "target": "current",
        }
