# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2016 Akretion (https://www.akretion.com).
#  @author Raphael Reverdy <raphael.reverdy@akretion.com>
#          David BEAL <david.beal@akretion.com>
#          Sébastien BEAU
##############################################################################

from openerp.tools.config import config
from openerp import models, fields, api
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp

from datetime import datetime, timedelta
import simplejson

TRS_CARRIER_TYPE = 'trs'


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def trs_get_meta(self):
        self.ensure_one()
        return self._get_packages_from_picking().trs_get_meta()

    def _trs_is_our(self):
        return self.carrier_id.type == TRS_CARRIER_TYPE

    def _trs_before_call(self, package_id, request):
        import pdb
        pdb.set_trace()
        request['parcel']['barcode'] = package_id.name
        request['parcel']['reference'] = (
            "%s/%s" % (package_id, len(self._get_packages_from_picking()))
        )
        return request

    def _trs_after_call(self, package_id, response):
        # response['meta'] (OrderedDict)
        # orderedDict.items() (list of tuples)
        # trs_meta (fields.Char)
        # can't serialize directly because we want to preserve order
        # json doesn't preserve order of keys in a {}
        meta = response['meta'].items()
        package_id.trs_meta = simplejson.dumps(meta)

        return {
            "data": response['zpl'],
            "tracking_id": "",
            "name": package_id.name,
        }

    def _trs_get_shipping_date(self, package_id):
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

        return shipping_date.strftime('%Y-%m-%d')


class ShippingLabel(models.Model):
    """ Child class of ir attachment to identify which are labels """
    _inherit = 'shipping.label'

    @api.model
    def _get_file_type_selection(self):
        """ Return a concatenated list of extensions of label file format
        plus file format from super
        This will be filtered and sorted in __get_file_type_selection
        :return: list of tuple (code, name)
        """
        file_types = super(ShippingLabel, self)._get_file_type_selection()
        new_types = [
            ('zpl2', 'ZPL2')
        ]
        file_types.extend(new_types)
        return file_types