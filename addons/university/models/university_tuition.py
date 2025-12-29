from odoo import models, fields, api


class Tuition(models.Model):
    _name = "university.tuition"
    _description = "Tuition model"

    # ====== #
    # FIELDS #
    # ====== #

    name = fields.Char(string="Reference", required=True, readonly=True, default="New")
    student_id = fields.Many2one("university.student", string="Student", required=True)
    university_id = fields.Many2one(
        "university.university", string="University", required=True
    )
    teacher_id = fields.Many2one("university.teacher", string="Teacher", required=True)
    subject_id = fields.Many2one("university.subject", string="Subject", required=True)
    grade_ids = fields.One2many("university.grade", "tuition_id", string="Grade")
    grade_count = fields.Integer(string="Grades", compute="_compute_count")
    dynamic_student_domain = fields.Char(
        compute="_compute_dynamic_student_domain", store=False
    )
    dynamic_teacher_domain = fields.Char(
        compute="_compute_dynamic_teacher_domain", store=False
    )
    dynamic_subject_domain = fields.Char(
        compute="_compute_dynamic_subject_domain", store=False
    )

    # ============ #
    # CRUD METHODS #
    # ============ #

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":

                # Get the subject code and year
                subject = self.env["university.subject"].browse(vals.get("subject_id"))
                subject_code = (subject.name or "GEN")[:3].upper()
                year = fields.Date.today().year

                # Get the base sequence
                seq_code = f"tuition.order.{subject_code}.{year}"

                # Search if the sequence exist
                sequence = self.env["ir.sequence"].search(
                    [("code", "=", seq_code)], limit=1
                )
                if not sequence:
                    sequence = self.env["ir.sequence"].create(
                        {
                            "name": f"Tuition {subject_code} {year}",
                            "code": seq_code,
                            "prefix": f"{subject_code}/{year}/",
                            "padding": 4,
                            "number_increment": 1,
                            "implementation": "standard",
                            "use_date_range": False,
                        }
                    )

                vals["name"] = sequence.next_by_id()

        return super(Tuition, self).create(vals)

    # ============== #
    # ACTION METHODS #
    # ============== #

    def action_view_grades(self):
        self.ensure_one()
        return {
            "name": "Grades",
            "type": "ir.actions.act_window",
            "res_model": "university.grade",
            "view_mode": "list,form",
            "domain": [("tuition_id", "=", self.id)],
            "target": "current",
        }

    # ================ #
    # COMPUTED METHODS #
    # ================ #

    @api.depends("grade_ids")
    def _compute_count(self):
        for tuition in self:
            tuition.grade_count = len(tuition.grade_ids)

    @api.depends("university_id")
    def _compute_dynamic_student_domain(self):
        for record in self:
            domain = []
            if record.university_id:
                domain.append(("university_id", "=", record.university_id.id))
            record.dynamic_student_domain = str(domain)

    @api.depends("university_id", "subject_id")
    def _compute_dynamic_teacher_domain(self):
        for record in self:
            domain = []
            if record.university_id:
                domain.append(("university_id", "=", record.university_id.id))
            if record.subject_id:
                domain.append(("subject_ids", "in", [record.subject_id.id]))
            record.dynamic_teacher_domain = str(domain)

    @api.depends("university_id", "teacher_id")
    def _compute_dynamic_subject_domain(self):
        for record in self:
            domain = []
            if record.university_id:
                domain.append(("university_id", "=", record.university_id.id))
            if record.teacher_id:
                domain.append(("teacher_ids", "in", [record.teacher_id.id]))
            record.dynamic_subject_domain = str(domain)

    # ================= #
    # ONCHANGED METHODS #
    # ================= #

    @api.onchange("student_id")
    def _onchange_student_id(self):

        if self.student_id:
            self.university_id = self.student_id.university_id

            if self.teacher_id and self.teacher_id.university_id != self.university_id:
                self.teacher_id = False

            if self.subject_id and self.teacher_id not in self.subject_id.teacher_ids:
                self.subject_id = False

    @api.onchange("teacher_id")
    def _onchange_teacher_id(self):

        if self.teacher_id:
            self.university_id = self.teacher_id.university_id

            if self.student_id and self.student_id.university_id != self.university_id:
                self.student_id = False

            if self.subject_id and self.subject_id not in self.teacher_id.subject_ids:
                self.subject_id = False

    @api.onchange("university_id")
    def _onchange_university_id(self):

        if self.university_id:

            if self.student_id and self.student_id.university_id != self.university_id:
                self.student_id = False

            if self.teacher_id and self.teacher_id.university_id != self.university_id:
                self.teacher_id = False

            if self.subject_id and self.subject_id.university_id != self.university_id:
                self.subject_id = False

    @api.onchange("subject_id")
    def _onchange_subject_id(self):
        if self.subject_id:
            self.university_id = self.subject_id.university_id

            if self.student_id and self.student_id.university_id != self.university_id:
                self.student_id = False

            if self.teacher_id and self.teacher_id not in self.subject_id.teacher_ids:
                self.teacher_id = False
