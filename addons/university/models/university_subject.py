from odoo import models, fields, api


class Subject(models.Model):
    _name = "university.subject"
    _description = "Subject model"

    # ====== #
    # FIELDS #
    # ====== #

    name = fields.Char(string="Name", required=True)
    university_id = fields.Many2one("university.university", string="University", required=True)
    teacher_ids = fields.Many2many(comodel_name="university.teacher", string="Teacher")
    tuition_ids = fields.One2many("university.tuition", "subject_id", string="Tuition")
    tuition_count = fields.Integer(string="Tuitions", compute="_compute_count")
    teacher_count = fields.Integer(string="Teachers", compute="_compute_count")

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
            "domain": [("subject_id", "=", self.id)],
            "target": "current",
        }

    def action_view_teachers(self):
        self.ensure_one()
        return {
            "name": "Teachers",
            "type": "ir.actions.act_window",
            "res_model": "university.teacher",
            "view_mode": "list,form",
            "domain": [("subject_id", "=", self.id)],
            "target": "current",
        }

    # ================ #
    # COMPUTED METHODS #
    # ================ #

    @api.depends("tuition_ids", "teacher_ids")
    def _compute_count(self):
        for subject in self:
            subject.tuition_count = len(subject.tuition_ids)
            subject.teacher_count = len(subject.teacher_ids)
