# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author David BEAL <david.beal@akretion.com>
#          Yannick VAUCHER, Camptocamp SA
#
##############################################################################

from openerp import models, fields
from openerp import api


class KuehneNagelConfigSettings(models.TransientModel):
    _name = 'kuehne.nagel.config.settings'
    _inherit = 'res.config.settings'

    def _default_company(self):
        return self.env.user.company_id

    company_id = fields.Many2one('res.company', 'Company', required=True, default=_default_company)
    kuehne_office_name = fields.Char(related='company_id.kuehne_office_name')
    kuehne_office_code = fields.Char(related='company_id.kuehne_office_code')
    kuehne_office_country_id = fields.Many2one(related='company_id.kuehne_office_country_id', comodel_name="res.country")
    kuehne_goods_name = fields.Char(related='company_id.kuehne_goods_name')
    kuehne_siret = fields.Char(related='company_id.kuehne_siret')
    kuehne_delivery_contract = fields.Selection(related='company_id.kuehne_delivery_contract')
    kuehne_service_system = fields.Selection(related='company_id.kuehne_service_system')
    kuehne_shipping_config = fields.Selection(related='company_id.kuehne_shipping_config')
    kuehne_vat_config = fields.Selection(related='company_id.kuehne_vat_config')
    kuehne_invoicing_contract = fields.Char(related='company_id.kuehne_invoicing_contract')

    @api.onchange('company_id')
    def onchange_company_id(self):

        if not self.company_id:
            #what's the point of this ?
            return
        company_id = self.company_id
        kuehne_siret = company_id.kuehne_siret
        kuehne_office_name = company_id.kuehne_office_name
        kuehne_office_code = company_id.kuehne_office_code
        kuehne_office_country_id = company_id.kuehne_office_country_id
        kuehne_goods_name = company_id.kuehne_goods_name
        kuehne_delivery_contract = company_id.kuehne_delivery_contract
        kuehne_service_system = company_id.kuehne_service_system
        kuehne_shipping_config = company_id.kuehne_shipping_config
        kuehne_vat_config = company_id.kuehne_vat_config
        kuehne_invoicing_contract = company_id.kuehne_invoicing_contract

    def button_send_image_to_printer(self, cr, uid, ids, context=None):
        """ Implement your own method according to printing solution
        """
        return KuehneNagelConfig().get_image_data()
