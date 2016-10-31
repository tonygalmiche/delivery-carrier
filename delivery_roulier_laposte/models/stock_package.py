# coding: utf-8
#  @author Raphael Reverdy <raphael.reverdy@akretion.com>
#          David BEAL <david.beal@akretion.com>
#          Sébastien BEAU
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models

CUSTOMS_MAP = {
    'gift': 1,
    'sample': 2,
    'commercial': 3,
    'document': 4,
    'other': 5,
    'return': 6,
}


class StockQuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    def _laposte_before_call(self, picking, request):
        def calc_package_price():
            return sum(
                [op.product_id.list_price * op.product_qty
                    for op in self.get_operations()]
            )
        # TODO _get_options is called fo each package by the result
        # is the same. Should be store after first call
        request['parcel'].update(picking._laposte_get_options(self))
        if request['parcel'].get('COD'):
            request['parcel']['CODAmount'] = self._get_cash_on_delivery(
                picking)
        request['service']['totalAmount'] = '%.f' % (  # truncate to string
            calc_package_price() * 100  # totalAmount is in centimes
        )
        request['service']['transportationAmount'] = 10  # how to set this ?
        request['service']['returnTypeChoice'] = 3  # do not return to sender
        request['to_address']['phone'] = '+33667228689'
        return request

    def _laposte_after_call(self, picking, response):
        # CN23 is included in the pdf url
        custom_response = {
            'name': response['parcelNumber'],
            'data': response.get('label'),
        }
        if response.get('url'):
            custom_response['url'] = response['url']
            custom_response['type'] = 'url'
        self.parcel_tracking = response['parcelNumber']
        return custom_response

    @api.multi
    def _laposte_get_customs(self, picking):
        """ see _roulier_get_customs() docstring
        """
        customs = self._roulier_get_customs(picking)
        customs['category'] = CUSTOMS_MAP.get(picking.customs_category)
        return customs

    @api.multi
    def _laposte_should_include_customs(self, picking):
        """Choose if customs infos should be included in the WS call.

        Return bool
        """
        # Customs declaration (cn23) is needed when :
        # dest is not in UE
        # dest is attached territory (like Groenland, Canaries)
        # dest is is Outre-mer
        #
        # see https://boutique.laposte.fr/_ui/doc/formalites_douane.pdf
        # Return true when not in metropole.
        international_products = (
            'COM', 'CDS',  # outre mer
            'COLI', 'CORI',  # colissimo international
            'BOM', 'BDP', 'BOS', 'CMT',  # So Colissimo international
        )
        return picking.carrier_code.upper() in international_products
