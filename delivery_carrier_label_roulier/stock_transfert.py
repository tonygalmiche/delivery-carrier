# coding: utf-8
# © 2016 David BEAL @ Akretion <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from openerp import _, api, models
from openerp.exceptions import Warning as UserError

_logger = logging.getLogger(__name__)
try:
    from roulier import roulier
except ImportError:
    _logger.debug('Cannot `import roulier`.')


class StockTransferDetails(models.TransientModel):
    _inherit = 'stock.transfer_details'

    @api.one
    def do_detailed_transfer(self):
        """ All carriers using roulier needs package, let's check
        """
        selection = self.picking_id._fields['carrier_type'].selection(self)
        # selection = [('dummy', 'DUMMY'), ('carrier1', 'Carrier 1')]
        map_selection = {x[0]: x[1] for x in selection}
        needs_package = False
        if map_selection[self.picking_id.carrier_type] in dir(roulier):
            needs_package = True
        for item in self.item_ids:
            if needs_package and not (
                    item.package_id or item.result_package_id):
                raise UserError(
                    _("All products to deliver for carrier '%s' \n"
                      "must be put in a parcel.")
                    % self.picking_id.carrier_id.name)
        return super(StockTransferDetails, self).do_detailed_transfer()
