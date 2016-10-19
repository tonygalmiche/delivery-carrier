# coding: utf-8
#  @author David BEAL <david.beal@akretion.com>
#          Yannick VAUCHER, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields
from openerp import api


class LaposteConfigSettings(models.TransientModel):
    _name = 'laposte.config.settings'
    _inherit = 'res.config.settings'

    def _default_company(self):
        return self.env.user.company_id

    company_id = fields.Many2one(
        'res.company', 'Company', required=True, default=_default_company)
    laposte_login = fields.Char(related='company_id.laposte_login')
    laposte_password = fields.Char(related='company_id.laposte_password')
    laposte_support_city = fields.Char(
        related='company_id.laposte_support_city')
    laposte_support_city_code = fields.Char(
        related='company_id.laposte_support_city_code')

    @api.onchange('company_id')
    def onchange_company_id(self):
        if not self.company_id:
            # what's the point of this ?
            return
        company = self.company_id
        self.laposte_login = company.laposte_login
        self.laposte_password = company.laposte_password
        self.laposte_support_city = company.laposte_support_city
        self.laposte_support_city_code = company.laposte_support_city_code
