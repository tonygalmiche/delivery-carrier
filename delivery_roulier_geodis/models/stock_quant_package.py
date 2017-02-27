# coding: utf-8
#  @author Raphael Reverdy <raphael.reverdy@akretion.com>
#          David BEAL <david.beal@akretion.com>
#           EBII MonsieurB <monsieurb@saaslys.com>
#          Sébastien BEAU
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, fields
import logging

_logger = logging.getLogger(__name__)


class StockQuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    geodis_shippingId = fields.Char()

    def _geodis_before_call(self, picking, request):
        # TODO _get_options is called fo each package by the result
        # is the same. Should be store after first call
        account = picking._get_account(self)
        service = account.get_data()
        request['service']['customerId'] = service['customerId']
        request['service']['agencyId'] = service['agencyId']
        request['service']['labelFormat'] = service['labelFormat']
        # TODO passer contexte multi compagny ou multi compte à la sequence"
        self._gen_shipping_id()
        request['service']['shippingId'] = self.geodis_shippingId
        request['service']['is_test'] = service['isTest']

        return request

    @api.model
    def _geodis_error_handling(self, payload, response):
        payload['auth']['password'] = '****'

        def _getmessage(payload, response):
            message = (
                u'Données transmises:\n%s\n\nExceptions levées %s\n'
                % (payload, response)
            )
            return message

        if 'Input error ' in response:
            # InvalidInputException
            # on met des clés plus explicites vis à vis des objets odoo
            suffix = (
                u"\nSignification des clés dans le contexte Odoo:\n"
                u"- 'to_address' : adresse du destinataire (votre client)\n"
                u"- 'from_address' : adresse de l'expéditeur (vous)")
            message = u'Données transmises:\n%s\n\nExceptions levées %s' \
                      u'\n%s' % (payload, response, suffix)
            return message
        elif 'message' in response:
            message = _getmessage(payload, response)
            return message
        elif response['status'] == 'error':
            message = _getmessage(payload, response)
            return message
        else:
            message = "Error Unknown"
            return message

    def _geodis_should_include_customs(self, picking):
        """Geodis does not return customs documents"""
        return False

    @api.multi
    def _gen_shipping_id(self):
        def gen_id():
            sequence = self.env['ir.sequence'].next_by_code(
                "geodis.nrecep.number")
            # this is prefixed by year_ so we split it befor use
            year, number = sequence.split('_')
            # pad with 0 to build an 8digits number (string)
            return '%08d' % int(number)

        for pack in self:
            pack.geodis_shippingId = (
                pack.geodis_shippingId or gen_id()
            )
        return True
