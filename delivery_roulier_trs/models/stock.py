# coding: utf-8
#  @author Raphael Reverdy <raphael.reverdy@akretion.com>
#          David BEAL <david.beal@akretion.com>
#          Sébastien BEAU
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import json
from collections import OrderedDict

from openerp import models, api

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _trs_get_auth(self, package):
        return {
        }

    def _trs_convert_address(self, partner):
        address = self._roulier_convert_address(partner)
        address['company'] = address.get('company', address.get('name'))
        return address

    def trs_get_meta(self):
        simplejson = json  # TODO change this !
        return (
            [OrderedDict(simplejson.loads(pack.trs_meta))
                for pack in self._get_packages_from_picking()]
        )
