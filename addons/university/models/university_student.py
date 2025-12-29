from odoo import models, fields, api
from odoo.tools import file_open
from odoo.exceptions import ValidationError

import base64, typing

if typing.TYPE_CHECKING:
    from odoo.addons.base.models.res_country import Country
    from odoo.addons.base.models.res_country_state import CountryState


class Student(models.Model):
    _name = "university.student"
    _description = "Student model"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # ====== #
    # FIELDS #
    # ====== #

    name = fields.Char(string="Name", required=True)
    email = fields.Char(string="Email", required=True)
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
    university_id = fields.Many2one("university.university", string="University", required=True)
    tutor_id = fields.Many2one("university.teacher", string="Tutor")
    tuition_ids = fields.One2many("university.tuition", "student_id", string="Tuition")
    grade_ids = fields.One2many("university.grade", "student_id", string="Grade")
    tuition_count = fields.Integer(string="Tuitions", compute="_compute_count")
    grade_count = fields.Integer(string="Grades", compute="_compute_count")
    avatar_128 = fields.Image(
        string="avatar 128",
        max_width=128,
        max_height=128,
        store=True,
        default=lambda self: self._get_default_avatar(),
    )
    user_id = fields.Many2one("res.users", string="UserId")
    dynamic_tutor_domain = fields.Char(
        compute="_compute_dynamic_tutor_domain", store=False
    )

    # ============ #
    # CRUD METHODS #
    # ============ #

    @api.model_create_multi
    def create(self, vals_list):
        students = super(Student, self).create(vals_list)
        for student in students:
            student._create_user_from_student()
        return students

    def write(self, vals):
        result = super(Student, self).write(vals)
        if "email" in vals and self.user_id:
            self.user_id.write(
                {
                    "login": self.email,
                    "email": self.email,
                }
            )
        if "name" in vals and self.user_id:
            self.user_id.write(
                {
                    "name": self.name,
                }
            )
        return result

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
            "domain": [("student_id", "=", self.id)],
            "target": "current",
        }

    def action_view_grades(self):
        self.ensure_one()
        return {
            "name": "Grades",
            "type": "ir.actions.act_window",
            "res_model": "university.grade",
            "view_mode": "list,form",
            "domain": [("student_id", "=", self.id)],
            "target": "current",
        }

    def action_print_pdf(self):
        self.ensure_one()
        report = self.env.ref("university.action_report_student_pdf")
        report_action = report.report_action(self, config=False)
        return report_action

    def action_send_pdf(self):
        self.ensure_one()
        template = self.env.ref(
            "university.student_mail_template", raise_if_not_found=False
        )
        attachment = self._generate_student_pdf()
        partner = self.env["res.partner"].search([("email", "=", self.email)], limit=1)
        if not partner:
            partner = self.env["res.partner"].create(
                {
                    "name": self.name,
                    "email": self.email,
                }
            )
        ctx = {
            "default_model": "university.student",
            "default_res_ids": [self.id],
            "default_use_template": bool(template),
            "default_template_id": template.id if template else False,
            "default_composition_mode": "comment",
            "default_attachment_ids": [(4, attachment.id)],
            "default_partner_ids": [(6, 0, [partner.id])],
        }
        return {
            "type": "ir.actions.act_window",
            "res_model": "mail.compose.message",
            "view_mode": "form",
#            "view_id": self.env.ref("university.university_student_send_wizard_form").id,
            "target": "new",
            "context": ctx,
        }

    # =============== #
    # HELPERS METHODS #
    # =============== #

    def send_report_preview(self):
        return self._send_report_preview()

    def _send_report_preview(self):
        try:
            attachment = self._generate_student_pdf()
            current_user = self.env.user

            template = self.env.ref(
                "university.student_mail_template", raise_if_not_found=False
            )

            if not template:
                return {"toast_message": "Email template not found"}

            if not current_user.email:
                return {"toast_message": "Your user account has no email configured"}

            template.with_context(
                preview_mode=True,
                current_user_name=current_user.name,
            ).send_mail(
                self.id,
                force_send=True,
                email_values={
                    "attachment_ids": [(4, attachment.id)],
                    "email_from": current_user.email,
                    "email_to": self.email,
                    "subject": f"Student Report - {self.name}",
                },
            )
            return {"toast_message": f"Preview email sent for {self.name}"}

        except Exception as e:
            return {"toast_message": f"Error sending email: {str(e)}"}

    def _generate_student_pdf(self):
        self.ensure_one()
        report = self.env.ref("university.action_report_student_pdf")
        pdf_data, _ = report._render_qweb_pdf(report_ref=report, res_ids=[self.id])
        attachment = self.env["ir.attachment"].create(
            {
                "name": f"Report {self.name}.pdf",
                "type": "binary",
                "datas": base64.b64encode(pdf_data),
                "res_model": "university.student",
                "res_id": self.id,
                "mimetype": "application/pdf",
            }
        )
        return attachment

    def _create_user_from_student(self):
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
            raise ValidationError("No se pudo crear el usuario: %s" % str(e))

    @api.model
    def _get_default_avatar(self):
        try:
            with file_open("university/static/src/img/student_default.png", "rb") as f:
                return base64.b64encode(f.read())
        except Exception:
            return False

    # ================ #
    # COMPUTED METHODS #
    # ================ #

    @api.depends("tuition_ids", "grade_ids")
    def _compute_count(self):
        for student in self:
            student.tuition_count = len(student.tuition_ids)
            student.grade_count = len(student.grade_ids)

    @api.depends("university_id")
    def _compute_dynamic_tutor_domain(self):
        for record in self:
            domain = []
            if record.university_id:
                domain.append(("university_id", "=", record.university_id.id))
            record.dynamic_tutor_domain = str(domain)

    # ================= #
    # ONCHANGED METHODS #
    # ================= #

    @api.onchange("university_id")
    def _onchange_univeristy_id(self):
        if self.tutor_id and self.tutor_id.university_id != self.university_id:
            self.tutor_id = False

    @api.onchange("tutor_id")
    def _onchange_tutor_id(self):
        if self.tutor_id and not self.university_id:
            self.university_id = self.tutor_id.university_id
