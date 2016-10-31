# coding: utf-8
#  @author Raphael Reverdy <raphael.reverdy@akretion.com>
#          David BEAL <david.beal@akretion.com>
#          Sébastien BEAU
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from openerp import models, fields, api, _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

from datetime import datetime, timedelta


_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    laposte_insur_recomm = fields.Selection(
        selection=[
            ('15000', 'Assurance 150 €'), ('30000', 'Assurance 300 €'),
            ('45000', 'Assurance 450 €'), ('60000', 'Assurance 600 €'),
            ('75000', 'Assurance 750 €'), ('90000', 'Assurance 900 €'),
            ('105000', 'Assurance 1050 €'), ('120000', 'Assurance 1200 €'),
            ('135000', 'Assurance 1350 €'), ('150000', 'Assurance 1500 €'),
            ('R1', 'Recommendation R1'), ('R2', 'Recommendation R2'),
            ('R3', 'Recommendation R3'),
        ], string=u"Assurance/recommandé")

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

    @api.model
    def _laposte_map_options(self):
        return {
            'NM': 'nonMachinable',
            'FCR': 'ftd',
            'COD': 'COD',
            'INS': 'insuranceValue',
        }

    @api.multi
    def _laposte_get_options(self, package):
        """Define options for the shippment.

        Like insurance, cash on delivery...
        It should be the same for all the packages of
        the shipment.
        """
        # should be extracted from a company wide setting
        # and oversetted in a view form
        self.ensure_one()
        options = self._roulier_get_options(package)
        if 'insuranceValue' in options:
            if self.laposte_insur_recomm[:1] == 'R':
                options['recommendationLevel'] = self.laposte_insur_recomm
                del options['insuranceValue']
            else:
                options['insuranceValue'] = self.laposte_insur_recomm
        if 'cod' in options:
            options['codAmount'] = 0
        return options

    @api.multi
    def _laposte_get_auth(self, package):
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
                30204:
                    u"La 2eme ligne d'adresse du client partenaire "
                    u"est vide ou invalide",
                30221:
                    u"Le telephone du client ne doit comporter que des "
                    u"chiffres ou le symbole +: convertissez tous vos N° de "
                    u"telephone au format standard a partir du menu suivant:\n"
                    u"Configuration > Technique > Telephonie > Reformate "
                    u"les numeros de telephone ",
                30100:
                    u"La seconde ligne d'adresse de l'expéditeur est "
                    u"vide ou invalide.",
            }
            message = response.get('message')
            param_message = {'ws_exception': message,
                             'resolution': ''}
            if message and message.get('id') in map_responses.keys():
                param_message['resolution'] = map_responses[
                    message['id']]
            ret_mess = _("Incident\n-----------\nReponse de Laposte:\n"
                         "%(ws_exception)s\n\n"
                         "Resolution\n-------------\n%(resolution)s"
                         % param_message)
        return ret_mess
