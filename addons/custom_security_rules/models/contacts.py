from odoo import models
from odoo.exceptions import ValidationError

import logging


class Contacts(models.Model):
    _inherit = 'res.partner'

    def write(self, vals):
        if len(self) == 1 and self.company_type == 'company':
            if not self.env.user.has_group('base.group_system'):
                raise ValidationError(
                    "No tiene permisos para modificar este contacto.")
        return super(Contacts, self).write(vals)
