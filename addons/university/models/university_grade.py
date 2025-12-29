from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Grade(models.Model):
    _name = "university.grade"
    _description = "Grade model"
    _rec_name = "name"

    # ====== #
    # FIELDS #
    # ====== #

    grade = fields.Float(string="Grade", required=True)
    student_id = fields.Many2one("university.student", string="Student", required=True)
    tuition_id = fields.Many2one("university.tuition", string="Tuition", required=True)
    exam_date = fields.Date(
        string="Exam Date", default=fields.Date.today, readonly=False, required=True
    )
    name = fields.Char(string="Grade Name", compute="_compute_name", store=True)

#    _sql_constraints = [
#        (
#            "grade_domain",
#            "CHECK(grade >= 0 AND grade <= 10)",
#            "The grade must be between 0 and 10",
#        )
#    ]

    # ================ #
    # ONCHANGE METHODS #
    # ================ #

    @api.onchange("tuition_id")
    def _onchange_tuition_id(self):
        if self.tuition_id and self.tuition_id.student_id:
            self.student_id = self.tuition_id.student_id

    # ================ #
    # COMPUTED METHODS #
    # ================ #

    @api.depends("student_id")
    def _compute_name(self):
        for rec in self:
            rec.name = f"{rec.student_id.name} - Grade" if rec.student_id else "Grade"

    # ================== #
    # CONSTRAINT METHODS #
    # ================== #

    @api.constrains("grade")
    def _check_precios_consistentes(self):
        for record in self:
            if (record.grade < 0 or record.grade > 10):
                raise ValidationError(
                    "The grade must be between 0 and 10"
                )
