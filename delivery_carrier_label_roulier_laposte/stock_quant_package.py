# coding: utf-8
#  @author Raphael Reverdy <raphael.reverdy@akretion.com>
#          David BEAL <david.beal@akretion.com>
#          Sébastien BEAU
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class StockQuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    # TODO: put this in base_delivery
    laposte_non_machinable = fields.Boolean(
        "Non Machinable",
        help="True if size of package is not standard (according to carrier)",
        default=False,
    )
