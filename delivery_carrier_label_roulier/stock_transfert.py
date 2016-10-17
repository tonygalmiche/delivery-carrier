# coding: utf-8
# © 2016 David BEAL @ Akretion <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from openerp import _, api, models
from openerp.exceptions import Warning as UserError

_logger = logging.getLogger(__name__)


class StockTransferDetails(models.TransientModel):
    _inherit = 'stock.transfer_details'

    @api.one
    def do_detailed_transfer(self):
        """ All carriers using roulier needs package, let's check
        """
        needs_package = self.picking_id._is_roulier()
        for item in self.item_ids:
            if needs_package and not (
                    item.package_id or item.result_package_id):
                raise UserError(
                    _("All products to deliver for carrier '%s' \n"
                      "must be put in a parcel.")
                    % self.picking_id.carrier_id.name)
        return super(StockTransferDetails, self).do_detailed_transfer()