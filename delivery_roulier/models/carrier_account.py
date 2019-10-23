#  @author David BEAL <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class CarrierAccount(models.Model):
    _inherit = 'carrier.account'

    delivery_type = fields.Selection(required=True)
