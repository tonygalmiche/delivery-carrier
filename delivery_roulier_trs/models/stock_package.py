# -*- coding: utf-8 -*-
# @author Raphael Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# import simplejson
import json
import logging
from openerp import models, fields, api

_logger = logging.getLogger(__name__)


class StockQuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    @api.multi
    def _trs_generate_parcel_tracking(self):
        for pack in self:
            pack.parcel_tracking = pack.name

    def _trs_before_call(self, picking, request):
        self._trs_generate_parcel_tracking()
        request['service']['shippingId'] = self.parcel_tracking

        packs = picking._get_packages_from_picking()
        pos = 1 + packs.ids.index(self.id)
        request['service']['reference2'] = "%s/%s" % (pos, len(packs))
        request['service']['reference1'] = picking.origin
        return request

    def _trs_after_call(self, picking, response):
        # response['attachment'] (OrderedDict)
        # orderedDict.items() (list of tuples)
        # trs_meta (fields.Char)
        # can't serialize directly because we want to preserve order
        # json doesn't preserve order of keys in a {}
        meta = response.get('attachment').items()
        # self.trs_meta = simplejson.dumps(meta)
        self.trs_meta = json.dumps(meta)  # TODO : change this !

        return {
            "data": response.get('payload'),
            "tracking_id": "",
            "name": self.name,
        }

    trs_meta = fields.Char(
        "meta",
        help="Needed for deposit slip (json OrderedDict)",
    )

