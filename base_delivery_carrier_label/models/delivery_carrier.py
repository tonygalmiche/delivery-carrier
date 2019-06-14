# Copyright 2012 Akretion <http://www.akretion.com>.
# Copyright 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(oldname='carrier_type')
    code = fields.Char(
        help="Delivery Method Code (according to carrier)",
    )
    description = fields.Text()
    available_option_ids = fields.One2many(
        comodel_name='delivery.carrier.option',
        inverse_name='carrier_id',
        string='Option',
    )
    is_oca_carrier_module = fields.Boolean(
        compute='_compute_oca_carrier_module', store=True)

    def _compute_oca_carrier_module(self):
        for rec in self:
            rec.is_oca_carrier_module = False
            if self.env.context.get('install_module'):
                module = self.env.context['install_module']
                if module:
                    module = self.env['ir.module.module'].search(
                        [('name', '=', module)])
                    if ('base_delivery_carrier_label' in
                            module.dependencies_id.mapped('name')):
                        rec.is_oca_carrier_module = True

    @api.multi
    def default_options(self):
        """ Returns default and available options for a carrier """
        options = self.env['delivery.carrier.option'].browse()
        for available_option in self.available_option_ids:
            if (available_option.mandatory or available_option.by_default):
                options |= available_option
        return options
