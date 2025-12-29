from odoo import models, fields, api


class StudentReport(models.Model):
    _name = "university.report.student"
    _description = "Reports"
    _auto = False

    # ====== #
    # FIELDS #
    # ====== #
    display_name = fields.Char(string="Name", compute="_compute_name")
    student_id = fields.Many2one("university.student", string="Student")
    tuition_id = fields.Many2one("university.tuition", string="Tuition")
    university_id = fields.Many2one("university.university", string="University")
    teacher_id = fields.Many2one("university.teacher", string="Teacher")
    department_id = fields.Many2one("university.department", string="Department")
    subject_id = fields.Many2one("university.subject", string="Subject")
    grade = fields.Float(string="Average grade", aggregator="avg")
    
    # ======= #
    # METHODS #
    # ======= #

    def init(self):
        self.env.cr.execute("DROP VIEW IF EXISTS university_report_student;")
        self.env.cr.execute(
            """
            CREATE OR REPLACE VIEW university_report_student AS (
                SELECT 
                    ROW_NUMBER() OVER() AS id,
                    tui.student_id AS student_id, 
                    tui.id AS tuition_id,   
                    tui.university_id AS university_id,
                    tui.teacher_id AS teacher_id,
                    t.department_id AS department_id,
                    tui.subject_id AS subject_id,
                    g.grade AS grade
                FROM university_grade g
                JOIN university_tuition tui ON g.tuition_id=tui.id
                JOIN university_teacher t ON tui.teacher_id=t.id   
            );
        """
        )

    def _compute_name(self):
        for record in self:
            if record.student_id:
                record.display_name = f"{record.student_id.name} - {record.tuition_id.name}"