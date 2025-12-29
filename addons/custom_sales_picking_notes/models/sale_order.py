from odoo import models, fields, api

class SaleOrderNotes(models.Model):
    _description = 'Notes to sale order'
    _inherit = 'sale.order'

    notes = fields.Text(string="Public notes")

    def write(self, vals):
        res = super(SaleOrderNotes, self).write(vals)
        if 'notes' in vals:
            for order in self:
                order.picking_ids.write({
                    'notes': order.notes
                })
        return res
