from odoo import models, fields, api, _
from odoo.tools import file_open

import base64, typing

if typing.TYPE_CHECKING:
    from odoo.addons.base.models.res_country import Country
    from odoo.addons.base.models.res_country_state import CountryState


class University(models.Model):
    _name = "university.university"
    _description = "University model"

    # ====== #
    # FIELDS #
    # ====== #

    name = fields.Char(string="Name", required=True)
    street = fields.Char(string="Street")
    city = fields.Char(string="City")
    state_id: "CountryState" = fields.Many2one(
        "res.country.state",
        string="State",
        ondelete="restrict",
        domain="[('country_id', '=?', country_id)]",
    )
    country_id: "Country" = fields.Many2one(
        "res.country", string="Country", ondelete="restrict"
    )
    country_code = fields.Char(related="country_id.code", string="Country Code")
    zip = fields.Char(string="Postal code")
    director_id = fields.Many2one("university.teacher", string="Director")
    tuition_ids = fields.One2many(
        "university.tuition", "university_id", string="Tuition"
    )
    student_ids = fields.One2many(
        "university.student", "university_id", string="Student"
    )
    teacher_ids = fields.One2many(
        "university.teacher", "university_id", string="Teacher"
    )
    department_ids = fields.One2many(
        "university.department", "university_id", string="Department"
    )
    tuition_count = fields.Integer(
        string="Tuitions", compute="_compute_count", store=True
    )
    student_count = fields.Integer(
        string="Students", compute="_compute_count", store=True
    )
    teacher_count = fields.Integer(
        string="Teachers", compute="_compute_count", store=True
    )
    department_count = fields.Integer(
        string="Departments", compute="_compute_count", store=True
    )
    avatar_128 = fields.Image(
        string="avatar 128",
        max_width=128,
        max_height=128,
        store=True,
        default=lambda self: self._get_default_avatar(),
    )

    # ============ #
    # CRUD METHODS #
    # ============ #

    def write(self, vals):
        if "director_id" in vals:
            old_director = self.mapped("director_id")
            old_director.write({"is_director": False})

            if vals["director_id"]:
                new_director = self.env["university.teacher"].browse(
                    vals["director_id"]
                )
                new_director.is_director = True
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        universities = super().create(vals_list)
        for university, vals in zip(universities, vals_list):
            director_id = vals.get("director_id")
            if director_id:
                teacher = self.env["university.teacher"].browse(director_id)
                teacher.is_director = True
        return universities

    # ============== #
    # ACTION METHODS #
    # ============== #

    def action_view_tuitions(self):
        self.ensure_one()
        return {
            "name": "Tuitions",
            "type": "ir.actions.act_window",
            "res_model": "university.tuition",
            "view_mode": "list,form",
            "domain": [("university_id", "=", self.id)],
            "target": "current",
        }

    def action_view_students(self):
        self.ensure_one()
        return {
            "name": "Students",
            "type": "ir.actions.act_window",
            "res_model": "university.student",
            "view_mode": "list,form",
            "domain": [("university_id", "=", self.id)],
            "target": "current",
        }

    def action_view_teachers(self):
        self.ensure_one()
        return {
            "name": "Teachers",
            "type": "ir.actions.act_window",
            "res_model": "university.teacher",
            "view_mode": "list,form",
            "domain": [("university_id", "=", self.id)],
            "target": "current",
        }

    def action_view_departments(self):
        self.ensure_one()
        return {
            "name": "Departments",
            "type": "ir.actions.act_window",
            "res_model": "university.department",
            "view_mode": "list,form",
            "domain": [("university_id", "=", self.id)],
            "target": "current",
        }

    # =============== #
    # HELPERS METHODS #
    # =============== #

    @api.model
    def _get_default_avatar(self):
        try:
            with file_open(
                "university/static/src/img/university_default.png", "rb"
            ) as f:
                return base64.b64encode(f.read())
        except Exception:
            return False

    # ================ #
    # COMPUTED METHODS #
    # ================ #

    @api.depends("tuition_ids", "student_ids", "teacher_ids", "department_ids")
    def _compute_count(self):
        for university in self:
            university.tuition_count = len(university.tuition_ids)
            university.student_count = len(university.student_ids)
            university.teacher_count = len(university.teacher_ids)
            university.department_count = len(university.department_ids)
