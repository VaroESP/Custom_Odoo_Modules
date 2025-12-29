from odoo import models, fields, api


class Department(models.Model):
    _name = "university.department"
    _description = "Department model"

    # ====== #
    # FIELDS #
    # ====== #

    name = fields.Char(string="Name", required=True)
    university_id = fields.Many2one("university.university", string="University", required=True)
    manager_id = fields.Many2one(
        "university.teacher",
        string="Department manager",
    )
    teacher_ids = fields.One2many(
        "university.teacher", "department_id", string="Teacher"
    )
    teacher_count = fields.Integer(string="Teachers", compute="_compute_count")

    # ============ #
    # CRUD METHODS #
    # ============ #

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record, vals in zip(records, vals_list):

            if vals.get("manager_id"):
                new_manager = self.env["university.teacher"].browse(vals["manager_id"])
                new_manager.is_manager = True
        return record

    @api.model
    def write(self, vals):
        for department in self:
            if "manager_id" in vals:
                old_manager = self.mapped("manager_id")
                old_manager.write({"is_manager": False})

                if vals["manager_id"]:
                    new_manager = self.env["university.teacher"].browse(
                        vals["manager_id"]
                    )
                    new_manager.is_manager = True
        return super().write(vals)

    # ============== #
    # ACTION METHODS #
    # ============== #

    def action_view_teachers(self):
        self.ensure_one()
        return {
            "name": "Teachers",
            "type": "ir.actions.act_window",
            "res_model": "university.teacher",
            "view_mode": "list,form",
            "domain": [("department_id", "=", self.id)],
            "target": "current",
        }

    # =================== #
    # COMPUTATED METHODS #
    # =================== #

    @api.depends("teacher_ids")
    def _compute_count(self):
        for department in self:
            department.teacher_count = len(department.teacher_ids)
