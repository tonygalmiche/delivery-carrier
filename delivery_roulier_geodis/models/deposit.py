# -*- coding: utf-8 -*-

from base64 import b64encode
import logging
from datetime import datetime

from openerp import models
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.translate import _
from openerp.exceptions import UserError

_logger = logging.getLogger(__name__)

try:
    from roulier import roulier
    from roulier.exception import (
        InvalidApiInput,
        # CarrierError
    )
except ImportError:
    _logger.debug('Cannot `import roulier`.')


class DepositSlip(models.Model):
    _inherit = "deposit.slip"

    def _geodis_prepare_data(self):
        """Create lines for each picking.

        In a EDI file order is important.
        Returns a dict per agencies

        @returns []
        """
        self.ensure_one()

        ships_per_agency = []
        pickagencies = {}

        # sort pickings per agencies
        for picking in self.picking_ids:
            account_data = picking._get_account(None).get_data()
            pickagency = pickagencies.get(account_data['agencyId'], {
                "pickings": [],
                "account_data": account_data
            })
            pickagency['pickings'].append(picking)
            pickagencies[account_data['agencyId']] = pickagency

        # do stuff on each agency
        shipments = []
        i = 0
        for agency_id, pickagency in pickagencies.iteritems():
            i += 1
            account_data = pickagency['account_data']

            # consolidate all pickings
            for picking in pickagency['pickings']:
                for ship in picking._geodis_prepare_edi():
                    shipments.append(ship)

            from_address = self._geodis_get_from_address(
                picking)
            agency_address = self._geodis_get_agency_address(
                picking, agency_id)

            service = {
                'depositId': '%s%s' % (self.id, i),
                'depositDate': datetime.strptime(
                    self.create_date,
                    DEFAULT_SERVER_DATETIME_FORMAT),
                'customerId': account_data['customerId'],
                'interchangeSender': account_data['interchangeSender'],
                'interchangeRecipient': account_data['interchangeRecipient'],
            }

            ships_per_agency.append({
                'shipments': shipments,
                'from_address': from_address,
                'agency_address': agency_address,
                'service': service
            })
        return ships_per_agency

    def _geodis_get_from_address(self, picking):
        """Return a dict of the sender."""
        partner = picking._get_sender(None)
        address = picking._convert_address(partner)
        address['siret'] = partner.siret
        return address

    def _geodis_get_agency_address(self, picking, agency_id):
        """Return a dict the agency."""
        partner = self._geodis_get_agency_partner(
            picking.carrier_id, agency_id)
        address = picking._convert_address(partner)
        address['siret'] = partner.siret
        return address

    def _geodis_get_agency_partner(self, delivery_carrier_id, agency_id):
        """Find a partner given an agency_id.

        An agency is:
            - a contact (res.partner)
            - child of carrier company
            - has ref field agency_id
        """
        carrier_hq = delivery_carrier_id.partner_id
        carrier_agency = self.env['res.partner'].search(
            [['parent_id', '=', carrier_hq.id], ['ref', '=', agency_id]])
        # we use internal reference
        if not carrier_agency:
            _logger.debug('No child agency, fallback to parent')
        return carrier_agency or carrier_hq

    def _geodis_create_edi_file(self, payload):
        """Create a edi file with headers and data.

        One agency per call.

        params:
            payload : roulier.get_api("edi")
        return: string
        """
        geo = roulier.get('geodis')
        try:
            edi = geo.get_edi(payload)  # io.ByteIO
        except InvalidApiInput as e:
            raise UserError(_(u'Bad input: %s\n' % e.message))
        return edi

    def _geodis_create_attachments(self):
        """Create EDI files in attachment."""
        payloads = self._geodis_prepare_data()
        for idx, payload_agency in enumerate(payloads, start=1):
            edi_file = self._geodis_create_edi_file(payload_agency)
            file_name = '%s_%s.txt' % (self.name, idx)
            vals = {
                'name': file_name,
                'res_id': self.id,
                'res_model': 'deposit.slip',
                'datas': b64encode(edi_file.encode('utf8')),
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
