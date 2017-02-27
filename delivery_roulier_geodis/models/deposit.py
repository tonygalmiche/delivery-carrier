# -*- coding: utf-8 -*-

from base64 import b64encode
import logging
from datetime import datetime

from openerp import models
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)
try:
    from roulier import roulier
except ImportError:
    _logger.debug('Cannot `import roulier`.')


class DepositSlip(models.Model):
    _inherit = "deposit.slip"

    def _geodis_prepare_data(self):
        """Create lines for each picking.

        The carrier is expecting a line per shipping.
        @returns []
        """
        self.ensure_one()

        ships_per_agency = []
        pickagencies = {}

        for picking in self.picking_ids:
            account_data = picking._get_account(None).get_data()
            pickagency = pickagencies.get(account_data['agencyId'], {
                "pickings": [],
                "account_data": account_data
            })
            pickagency['pickings'].append(picking)
            pickagencies[account_data['agencyId']] = pickagency

        shipments = []
        for agencyId, pickagency in pickagencies.iteritems():
            account_data = pickagency['account_data']

            for picking in pickagency['pickings']:
                for ship in picking._geodis_prepare_edi():
                    shipments.append(ship)

            import pdb
            pdb.set_trace()
            from_partner = picking._get_sender(None)
            agency_partner = self.get_agency_partner(
                picking.carrier_id, agencyId)

            from_address = picking._convert_address(from_partner)
            agency_address = picking._convert_address(agency_partner)

            service = {
                'deposit': self.name,
                'depositDate': datetime.strptime(
                    self.create_date,
                    DEFAULT_SERVER_DATETIME_FORMAT),
                'customerId': account_data['customerId'],
                'interchangeSender': account_data['interchangeSender'],
                'interchangeReceiver': account_data['interchangeReceiver'],
            }

            ships_per_agency.append({
                'shipments': shipments,
                'from_address': from_address,
                'agency_address': agency_address,
                'service': service
            })
        return ships_per_agency

    def get_agency_partner(self, delivery_carrier_id, agency_id):
        carrier_hq = delivery_carrier_id.partner_id
        carrier_agency = self.env['res.partner'].search(
            [['parent_id', '=', carrier_hq.id], ['ref', '=', agency_id]])
        # we use internal reference
        if not carrier_agency:
            _logger.debug('No child agency, fallback to parent')
        return carrier_agency or carrier_hq

    def _geodis_create_edi_file(self, payload):
        """Create a edi file with headers and data.

        params:
            payload : [OrderedDict]
        return: io.ByteIO
        """
        geo = roulier.get('geodis')
        edi = geo.get_edi(payload)  # io.ByteIO
        return edi

    def _geodis_create_attachments(self):
        """Create a slip and add it in attachment."""
        payloads = self._geodis_prepare_data()
        import pdb
        pdb.set_trace()
        for payload in payloads:
            edi_file = self._geodis_create_edi_file(payload)
            file_name = '%s.txt' % self.name
            vals = {
                'name': file_name,
                'res_id': self.id,
                'res_model': 'deposit.slip',
                'datas': b64encode(edi_file),
                'datas_fname': file_name,
                'type': 'binary',
            }
            self.env['ir.attachment.metadata'].create(vals)
        return True

    def create_edi_file(self):
        self.ensure_one()
        if self.carrier_type == 'geodis':
            return self._geodis_create_attachments()
        else:
            return super(DepositSlip, self).create_edi_file()
