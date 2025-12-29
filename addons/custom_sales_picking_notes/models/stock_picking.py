from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class StockPickingNotes(models.Model):
    _description = 'Notes to stock picking'
    _inherit = 'stock.picking'

    notes = fields.Text(string="public notes", readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            sale_order = self.env['sale.order'].sudo().search(
                [('name', '=', vals['origin'])], limit=1)
            if sale_order.id and sale_order.notes:
                vals['notes'] = sale_order.notes
        return super(StockPickingNotes, self).create(vals_list)