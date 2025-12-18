from odoo import models, api, fields


class WorkshopMaintenanceReport(models.AbstractModel):
    _name = "report.workshop.workshop_maintenance_report"
    _description = "Workshop Maintenance Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env["workshop.maintenance"].browse(docids)
        today = fields.Date.today()
        return {
            "doc_ids": docids,
            "doc_model": "workshop.maintenance",
            "docs": docs,
            "today": today,
        }
