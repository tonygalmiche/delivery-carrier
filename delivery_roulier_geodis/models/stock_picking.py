# coding: utf-8
#  @author Raphael Reverdy <raphael.reverdy@akretion.com>
#          David BEAL <david.beal@akretion.com>
#          Sébastien BEAU
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from openerp import models, api, fields, _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import Warning as UserError

from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)
try:
    from roulier import roulier
    from roulier.exception import (
        InvalidApiInput,
        CarrierError
    )
except ImportError:
    _logger.debug('Cannot `import roulier`.')


GEODIS_DEFAULT_PRIORITY = {
    'MES': "3",
    'MEI': "3",
    'CXI': "1",
    'CX': "1",
    'EEX': "1",
}

GEODIS_DEFAULT_TOD = {
    'MES': 'P',
    'MEI': 'DAP',
    'CXI': 'P',
    'EEX': 'DAP',
}


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    geodis_shippingid = fields.Char(help="Shipping Id in Geodis terminology")

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
        """Truncate address and name to 35 chars."""
        address = self._roulier_convert_address(partner) or {}
        # get_split_adress from partner_helper module
        streets = partner._get_split_address(partner, 3, 35)
        address['street1'], address['street2'], address['street3'] = streets
        for field in ('name', 'city'):
            address[field] = address[field][0:35]
        return address

    def _geodis_get_priority(self, package):
        """Define options for the shippment."""
        return GEODIS_DEFAULT_PRIORITY.get(self.carrier_code, '')

    def _geodis_get_options(self, package):
        """Compact geodis options.

        Options are passed as string. it obey some custom
        binding like RDW + AAO = AWO.
        It should be implemented here. For the moment, only
        one option can be passed.
        """
        options = self._roulier_get_options(package)
        actives = [
            option for option in options.keys()
            if options[option]]
        return actives and actives[0] or []

    def _geodis_get_notifications(self, package):
        options = self._get_options(package)
        recipient = self._convert_address(
            self._get_receiver(package))
        if 'RDW' in options:
            if recipient['email']:
                if recipient['phone']:
                    return 'P'
                else:
                    return 'M'
            else:
                if recipient['phone']:
                    return 'S'
                else:
                    raise UserError(_(
                        "Can't set up a rendez-vous wihout mail or tel"))

    def _geodis_get_service(self, package):
        service = self._roulier_get_service(package)
        service['option'] = self._get_options(package)
        service['notifications'] = self._geodis_get_notifications(package)
        return service

    def _geodis_prepare_edi(self):
        """Return a list."""
        self.ensure_one()
        picking = self

        packages = picking._get_packages_from_picking()
        parcels = [{
            "barcode": pack.geodis_cab,
            "weight": pack.weight
        } for pack in packages]

        return {
            "product": picking.carrier_code,
            "productOption": picking._get_options(None),
            "productPriority": picking._geodis_get_priority(None),
            "notifications": picking._geodis_get_notifications(None),
            "productTOD": GEODIS_DEFAULT_TOD[picking.carrier_code],
            "to_address": self._convert_address(
                picking._get_receiver(None)),
            "reference1": picking.origin,
            "reference2": "",
            "reference3": "",
            "shippingId": picking.geodis_shippingid,
            "parcels": parcels
        }

    def _geodis_check_address(self):
        # check address
        picking = self
        package = self.env['stock.quant.package'].create({})
        package.carrier_id = picking.carrier_id
        roulier_instance = roulier.get(picking.carrier_type)
        payload = roulier_instance.api('findLocalite')
        receiver = picking._get_receiver(self)
        payload['auth'] = picking._get_auth(self)
        payload['to_address'] = picking._convert_address(receiver)
        try:
            # api call
            ret = roulier_instance.get(payload, 'findLocalite')
        except InvalidApiInput as e:
            raise UserError(package._invalid_api_input_handling(payload, e))
        except CarrierError as e:
            raise UserError(package._carrier_error_handling(payload, e))

        # give result to someone else
        return ret

    def _geodis_ensure_address(self):
        """Returns true if city and zip are validated by geodis."""
        try:
            addresses = self._geodis_check_address(self)
        except CarrierError:
            return False
        if len(addresses != 1):
            return False
        addr = addresses[0]
        receiver = self._get_receiver(self)
        dest = self._convert_address(receiver)
        if addr['city'].upper() != dest['city'].upper():
            return False
        if addr['zip'] != dest['zip']:
            return False
        return True

    @api.multi
    def _gen_shipping_id(self):
        """Generate a shipping id.

        Shipping id is persisted on the picking and it's
        calculated from a sequence since it should be
        8 char long and unique for at least 1 year
        """
        def gen_id():
            sequence = self.env['ir.sequence'].next_by_code(
                "geodis.nrecep.number")
            # this is prefixed by year_ so we split it befor use
            year, number = sequence.split('_')
            # pad with 0 to build an 8digits number (string)
            return '%08d' % int(number)

        for picking in self:
            picking.geodis_shippingid = (
                picking.geodis_shippingid or gen_id()
            )
        return True
