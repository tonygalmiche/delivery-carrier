# coding: utf-8
#  @author Raphael Reverdy <raphael.reverdy@akretion.com>
#          David BEAL <david.beal@akretion.com>
#          Sébastien BEAU
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from openerp import models
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _geodis_get_shipping_date(self, package_id):
        """Estimate shipping date."""
        self.ensure_one()
        shipping_date = self.min_date
        if self.date_done:
            shipping_date = self.date_done

        shipping_date = datetime.strptime(
            shipping_date, DEFAULT_SERVER_DATETIME_FORMAT)

        tomorrow = datetime.now() + timedelta(1)
        if shipping_date < tomorrow:
            # don't send in the past
            shipping_date = tomorrow

        return shipping_date.strftime('%Y%m%d')

    def _geodis_convert_address(self, partner):
        """Truncate address to 35 chars."""
        address = self._roulier_convert_address(partner) or {}
        # get_split_adress from partner_helper module
        streets = partner._get_split_address(partner, 3, 35)
        address['street1'], address['street2'], address['street3'] = streets
        return address

    def _geodis_prepare_edi(self):
        """Return a dict."""
        self.ensure_one()
        picking = self
        # because we ship per pack and not per picking:
        packages = picking._get_packages_from_picking()
        data = []

        for pack in packages:
            parcels = [{
                "barcode": "jvjkmqfjmfjq",  # pack.barcode,
                "weight": pack.weight
            }]

            data += [{
                "product": picking.carrier_code,
                "productOption": "",  # product["option"],
                "to_address": self._convert_address(
                    picking._get_receiver(pack)),
                "reference1": picking.origin,
                "reference2": "DEV-X-Y",
                "reference3": "",
                "shippingId": pack.geodis_shippingId,
                "parcels": parcels
            }]
        return data
