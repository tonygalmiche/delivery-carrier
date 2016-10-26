# coding: utf-8
# © 2016 David BEAL <david.beal@akretion.com>
#        Raphael REVERDY <raphael.reverdy@akretion.com>
#        Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class AbstractDropoffColiposte(models.AbstractModel):
    _name = 'abstract.dropoff.coliposte'
    _inherit = 'abstract.dropoff.site'

    lot_routing = fields.Char(
        string='Lot routing',
        help="Lot d'acheminement pour 'LaPoste'")
    distri_sort = fields.Char(
        string='Distri sort',
        help="Distribution sort pour 'LaPoste'")
    version_plan = fields.Char(
        string='Version plan',
        help="Plan version pour 'LaPoste'")


class PartnerDropoffSite(models.Model):
    _inherit = ['partner.dropoff.site', 'abstract.dropoff.coliposte']
    _name = 'partner.dropoff.site'
    _dropoff_type = 'laposte'
