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

KUEHNE_CARRIER_TYPE = 'kuehne'


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    kuehne_meta = fields.Text(
        "meta",
        help="Needed for deposit slip",
    )
    kuehne_meta_footer = fields.Text(
        "meta footer",
        help="Needed for deposit slip",
    )
    kuehne_delivery_type = fields.Selection([
        ('d', 'Direct Delivery'),
        ('r', 'Appointment')],
        'Delivery Type',
        default='r')


    @api.multi
    def kuehne_get_meta(self):
        self.ensure_one()
        parcels = self._get_packages_from_picking().kuehne_get_meta()
        meta = '%s\n%s\n%s' % (self.kuehne_meta, parcels, self.kuehne_meta_footer)
        return meta

    def _kuehne_is_our(self):
        return self.carrier_id.type == KUEHNE_CARRIER_TYPE

    def _kuehne_get_directional_code(self):
        directional_codes = self.env['kuehne.directional.code'].search([
            ('start_date', '<=', fields.Date.today()),
            ('country_from_id', '=', self.warehouse.country_id.id),
            ('country_to_id', '=', self.partner_id.country_id.id),
            ('first_zip', '<=', self.partner_id.zip),
            ('last_zip', '>=', self.partner_id.zip)
        ])
        if directional_codes:
            if len(directional_codes) == 1:
                return {
                    'office': directional_codes.office_code,
                    'round': directional_codes.office_round,
                    'export_hub': directional_codes.export_hub
                }
        return {'office': '', 'round': '', 'export_hub': ''}

    def _kuehne_before_call(self, package_id, request):
        directional_code = self._kuehne_get_directional_code()
        warehouse = self.picking_type_id.warehouse_id
        office_name = "KUEHNE NAGEL ROAD / AG : %s %s %s" % (
            self.warehouse.kuehne_office_country_id.code.upper(),
            self.warehouse.kuehne_office_code,
            self.warehouse.kuehne_office_name)
        sender_name = "%s/%s/%s/%s" % (
            self.warehouse.name,
            self.warehouse.country_id.code.upper(),
            self.warehouse.zip,
            self.warehouse.city)
        request.update({
            'service': {
                'shippingDate': self.date_done,
                'goodsName': self.warehouse.kuehne_goods_name,
                'epalQuantity': 0,
                'shippingOffice': directional_code['office'],
                'shippingRound': directional_code['round'],
                'shippingName': self.name,
                'mhuQuantity': len(self._get_packages_from_picking()),
                'weight': self.weight,
                'volume': self.volume,
                'deliveryContract': self.warehouse.kuehne_delivery_contract,
                'exportHub': directional_code['export_hub'],
                'orderName': self.sale_id.name,
                'shippingConfig': self.warehouse.kuehne_shipping_config.upper(),
                'vatConfig': self.warehouse.kuehne_vat_config.upper(),
                'invoicingContract': self.warehouse.kuehne_invoicing_contract,
                'deliveryType': self.kuehne_delivery_type.upper(),
                'serviceSystem': self.warehouse.kuehne_service_system,
                'note': self.note,
                'kuehneOfficeName': office_name
            }
        })
        request['to_address']['contact'] = self.partner_id.name
        request['from_address']['companyName'] = sender_name
        package_ids = self._get_packages_from_picking().ids
        package_ids.sort()
        count = 1
        for pack_id in package_ids:
            if pack_id == package_id.id:
                break
            count += 1
        request['parcel'].update({
            'barcode': package_id.name,
            'number': count
        })
        return request

    def _kuehne_after_call(self, package_id, response):
        package_id.kuehne_meta = response['parcel']
        self.kuehne_meta = response['line']
        self.kuehne_meta_footer = response['footer']
        return {
            "data": response['epl'],
            "tracking_id": "",
            "name": package_id.name,
        }

    def _kuehne_get_shipping_date(self, package_id):
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

    @api.multi
    def _kuehne_get_options(self):
        """Define options for the shippment.

        Like insurance, cash on delivery...
        It should be the same for all the packages of
        the shippment.
        """
        # should be extracted from a company wide setting
        # and oversetted in a view form
        self.ensure_one()
        option = {}
        # TODO implement here
        # if self.option_ids:
        #    for opt in self.option_ids:
        #        opt_key = str(opt.tmpl_option_id['code'].lower())
        #        option[opt_key] = True
        return option
