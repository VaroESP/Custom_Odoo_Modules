from odoo import models, fields, api
from odoo.tools import file_open
import base64


class Teacher(models.Model):
    _name = "university.teacher"
    _description = "Teacher model"

    # ====== #
    # FIELDS #
    # ====== #

    name = fields.Char(string="Name", required=True)
    is_manager = fields.Boolean(string="Is manager", default=False)
    is_tutor = fields.Boolean(string="Is tutor", default=False)
    is_director = fields.Boolean(string="Is director", default=False)
    student_ids = fields.One2many("university.student", "tutor_id", string="Tutors")
    university_id = fields.Many2one("university.university", string="University", required=True)
    department_id = fields.Many2one("university.department", string="Department", required=True)
    subject_ids = fields.Many2many(comodel_name="university.subject", string="Subjects")
    tuition_ids = fields.One2many("university.tuition", "teacher_id", string="Tuitions")
    student_count = fields.Integer(string="Students", compute="_compute_count")
    avatar_128 = fields.Image(
        string="avatar 128",
        max_width=128,
        max_height=128,
        store=True,
        default=lambda self: self._get_default_avatar(),
    )
    dynamic_department_domain = fields.Char(
        compute="_compute_dynamic_department_domain", store=False
    )

    # ============ #
    # CRUD METHODS #
    # ============ #

    @api.model_create_multi
    def create(self, vals_list):
        teachers = super().create(vals_list)
        return teachers

    # ============== #
    # ACTION METHODS #
    # ============== #

    def action_view_students(self):
        self.ensure_one()
        return {
            "name": "Students",
            "type": "ir.actions.act_window",
            "res_model": "university.student",
            "view_mode": "list,form",
            "domain": [("tutor_id", "=", self.id)],
            "target": "current",
        }

    # =============== #
    # HELPERS METHODS #
    # =============== #

    @api.model
    def _get_default_avatar(self):
        try:
            with file_open("university/static/src/img/teacher_default.png", "rb") as f:
                return base64.b64encode(f.read())
        except Exception:
            return False

    # ================ #
    # COMPUTED METHODS #
    # ================ #

    @api.depends("student_ids")
    def _compute_count(self):
        for teacher in self:
            teacher.student_count = len(teacher.student_ids)

    @api.depends("university_id")
    def _compute_dynamic_department_domain(self):
        for record in self:
            domain = []
            if record.university_id:
                domain.append(("university_id", "=", record.university_id.id))
            record.dynamic_department_domain = str(domain)

    # ================= #
    # ONCHANGED METHODS #
    # ================= #

    @api.onchange("university_id")
    def _onchange_univeristy_id(self):
        if (
            self.department_id
            and self.department_id.university_id != self.university_id
        ):
            self.department_id = False

    @api.onchange("department_id")
    def _onchange_department_id(self):
        if self.department_id:
            self.university_id = self.department_id.university_id
