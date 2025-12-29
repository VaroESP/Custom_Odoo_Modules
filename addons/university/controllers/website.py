from odoo import http
from odoo.http import request


class ControllerWebsite(http.Controller):

    @http.route("/", auth="public", website=True)
    def home_page(self, **kwargs):
        return request.render("university.university_website_home", {})

    @http.route("/universities", auth="public", website=True)
    def university_page(self, **kwargs):
        universities = request.env["university.university"].sudo().with_context(bin_size=False).search([])

        return request.render(
            "university.university_website_universities",
            {
                "universities": universities,
            },
        )

    @http.route(
        '/university/<model("university.university"):university>/teachers',
        auth="public",
        website=True,
    )
    def teacher_page(self, university, **kwargs):
        teachers = (
            request.env["university.teacher"]
            .sudo()
            .search([("university_id", "=", university.id)])
        )
        return request.render(
            "university.university_website_teachers",
            {
                "university": university,
                "teachers": teachers,
            },
        )

    @http.route("/my/grades", auth="user", website=True)
    def grade_page(self, **kwargs):
        current_user = request.env.user

        student = (
            request.env["university.student"]
            .sudo()
            .search([("user_id", "=", current_user.id)], limit=1)
        )

        grades = (
            request.env["university.grade"]
            .sudo()
            .search([("student_id", "=", student.id)])
        )
        if grades:
            return request.render(
                "university.university_website_grades",
                {"student": student, "grades": grades},
            )
