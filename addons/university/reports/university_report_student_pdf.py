from odoo import models, fields, api


class StudentReportPdf(models.Model):
    _name = "university.report.student.pdf"
    _description = "Reports"
    _auto = False

    # ====== #
    # FIELDS #
    # ====== #

    student_id = fields.Many2one("university.student", string="Student")
    teacher_id = fields.Many2one("university.teacher", string="Teacher")
    subject_id = fields.Many2one("university.subject", string="Subject")
    average_grade = fields.Float(string="Average Grade")

    # ======= #
    # METHODS #
    # ======= #

    def init(self):
        self.env.cr.execute("DROP VIEW IF EXISTS university_report_student_pdf;")
        self.env.cr.execute(
            """
            CREATE OR REPLACE VIEW university_report_student_pdf AS (
                SELECT 
                    ROW_NUMBER() OVER() AS id,
                    g.student_id as student_id,
                    tui.subject_id as subject_id,
                    tui.teacher_id as teacher_id,
                    AVG(g.grade) as average_grade  
                FROM university_grade g
                JOIN university_tuition tui ON g.tuition_id=tui.id
                GROUP BY g.student_id, tui.subject_id, tui.teacher_id 
            );
        """
        )

    @api.model
    def get_student_grades_summary(self, student_id):
        return self.search([("student_id", "=", student_id)])
