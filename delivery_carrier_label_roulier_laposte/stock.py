# coding: utf-8
#  @author Raphael Reverdy <raphael.reverdy@akretion.com>
#          David BEAL <david.beal@akretion.com>
#          Sébastien BEAU
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

from datetime import datetime, timedelta


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    laposte_custom_category = fields.Selection(
        selection=[
            ("1", "Gift"),
            ("2", "Samples"),
            ("3", "Commercial Goods"),
            ("4", "Documents"),
            ("5", "Other"),
            ("6", "Goods return"),
        ],
        help="Type of sending for the customs",
        default="3")  # todo : extraire ca dans roulier_international

    def _laposte_before_call(self, package_id, request):
        def calc_package_price(package_id):
            return sum(
                [op.product_id.list_price * op.product_qty
                    for op in package_id.get_operations()]
            )
        request['parcel']['nonMachinable'] = package_id.laposte_non_machinable
        request['service']['totalAmount'] = '%.f' % (  # truncate to string
            calc_package_price(package_id) * 100  # totalAmount is in centimes
        )
        request['service']['transportationAmount'] = 10  # how to set this ?
        request['service']['returnTypeChoice'] = 3  # do not return to sender
        return request

    def _laposte_after_call(self, package_id, response):
        # CN23 is included in the pdf url
        custom_response = {
            'name': response['parcelNumber'],
            'data': response.get('label'),
        }
        if response.get('url'):
            custom_response['url'] = response['url']
            custom_response['type'] = 'url'
        return custom_response

    def _laposte_get_shipping_date(self, package_id):
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
    def _laposte_get_options(self):
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

    @api.multi
    def _laposte_get_auth(self):
        """Fetch a laposte login/password.

        Currently it's global for the company.
        TODO:
            * allow multiple accounts
            * store the password securely
            * inject it via ENVIRONMENT variable
        """
        self.ensure_one()
        return {
            'login': self.company_id.laposte_login,
            'password': self.company_id.laposte_password
        }

    @api.multi
    def _laposte_get_customs(self, package_id):
        """Format customs infos for each product in the package.

        The decision whether to include these infos or not is
        taken in _should_include_customs()

        Returns:
            dict.'articles' : list with qty, weight, hs_code
            int category: gift 1, sample 2, commercial 3, ...
        """
        articles = []
        for operation in package_id.get_operations():
            article = {}
            articles.append(article)
            product = operation.product_id
            # stands for harmonized_system
            hs = product.product_tmpl_id.get_hs_code_recursively()

            article['quantity'] = '%.f' % operation.product_qty
            article['weight'] = (
                operation.get_weight() / operation.product_qty)
            article['originCountry'] = product.origin_country_id.code
            article['description'] = hs.description
            article['hs'] = hs.hs_code
            article['value'] = product.list_price  # unit price is expected
            # todo : extraire ca dans roulier_international

        category = self.laposte_custom_category
        return {
            "articles": articles,
            "category": category,
        }

    @api.multi
    def _laposte_should_include_customs(self, package_id):
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
        return self.carrier_code.upper() in international_products

    # voir pour y mettre en champ calcule ?
    @api.multi
    def _laposte_get_parcel_tracking(self):
        """Get the list of tracking numbers.

        Each package may have his own tracking number
        returns:
            list of string
        """
        self.ensure_one()
        return [pack.parcel_tracking
                for pack in self._get_packages_from_picking()
                if pack.parcel_tracking]

    # helpers
    @api.model
    def _laposte_convert_address(self, partner):
        """Convert a partner to an address for roulier.

        params:
            partner: a res.partner
        return:
            dict
        """
        address = self._roulier_convert_address(partner) or {}
        # get_split_adress from partner_helper module
        streets = partner._get_split_address(partner, 3, 38)
        address['street'], address['street2'], address['street3'] = streets
        # TODO manage in a better way if partner_firstname is installed
        address['firstName'] = '.'
        if 'partner_firstname' in self.env.registry._init_modules \
                and partner.firstname:
            address['firstName'] = partner.firstname
        return address

    @api.model
    def _laposte_error_handling(self, payload, response):
        ret_mess = u'Données transmises:\n%s\n\nExceptions levées%s\n%s'
        if response.get('api_call_exception'):
            # InvalidInputException
            # on met des clés plus explicites vis à vis des objets odoo
            suffix = (u"\nSignification des clés dans le contexte Odoo:\n"
                      u"- 'to_address' correspond à 'adresse client'\n"
                      u"- 'from_address' correspond à 'adresse de la société'")
            password = payload['auth']['password']
            message = u'Données transmises:\n%s\n\nExceptions levées%s\n%s' % (
                payload, response, suffix)
            message = message.replace(password, '****')
            return message
        elif response.get('message'):
            # Webservice error
            # on contextualise les réponses ws aux objets Odoo
            map_responses = {
                u"Le num\xe9ro / libell\xe9 de voie du destinataire n'a pas "
                u"\xe9t\xe9 transmis":
                u"La 2eme rue du client partenaire est vide ou invalide",

                u"Le num\xe9ro de portable du destinataire est incorrect":
                u"Le telephone du client ne doit comporter que des chiffres "
                u"ou le symbole +: convertissez tous vos N° de telephone "
                u"au format standard a partir du menu suivant:\n"
                u"Configuration > Technique > Telephonie > Reformate "
                u"les numeros de telephone ",
            }
            message = response.get('message')
            param_message = {'ws_exception': response['message'],
                             'resolution': ''}
            if message and message.get('message') in map_responses.keys():
                param_message['resolution'] = map_responses[
                    message['message']]
            ret_mess = _("Incident\n-----------\nReponse de Laposte:\n"
                         "%(ws_exception)s\n\n"
                         "Resolution\n-------------\n%(resolution)s"
                         % param_message)
        return ret_mess
