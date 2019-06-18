# Copyright 2014-2015 Akretion <http://www.akretion.com>
# Copyright 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp
from ..decorator import implemented_by_carrier

_logger = logging.getLogger(__name__)


class StockQuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    parcel_tracking = fields.Char(string='Parcel Tracking')
    parcel_tracking_uri = fields.Char(
        help="Link to the carrier's tracking page for this package.",
    )
    total_weight = fields.Float(
        digits=dp.get_precision('Stock Weight'),
        help="Total weight of the package in kg, including the "
             "weight of the logistic unit."
    )

    @api.depends('total_weight')
    def _compute_weight(self):
        """ Use total_weight if defined
        otherwise fallback on the computed weight
        """
        to_do = self.browse()
        for pack in self:
            if pack.total_weight:
                pack.weight = pack.total_weight
            elif not pack.quant_ids:
                # package.pack_operations would be too easy
                operations = self.env['stock.move.line'].search([
                    ('result_package_id', '=', pack.id),
                    ('product_id', '!=', False),
                ])

                # we make use get_weight with  @api.multi instead of
                # sum([op.get_weight for op in operations])

                # sum of the pack_operation
                payload_weight = operations.get_weight()

                # sum and save in package
                pack.weight = payload_weight

            else:
                to_do |= pack
        if to_do:
            super(StockQuantPackage, to_do)._compute_weight()

    @api.multi
    def _complete_name(self, name, args):
        res = super()._complete_name(name, args)
        for pack in self:
            if pack.parcel_tracking:
                res[pack.id] += ' [%s]' % pack.parcel_tracking
            if pack.weight:
                res[pack.id] += ' %s kg' % pack.weight
        return res

    @api.multi
    def open_website_url(self):
        """Open website for parcel tracking.
        Each carrier should implement _get_tracking_link
        There is low chance you need to override this method.
        returns:
            action
        """
        self.ensure_one()
        if not self.parcel_tracking:
            raise UserError(
                _("Cannot open tracking URL for this carrier "
                  "because this package "
                  "doesn't have a tracking number."))
        return {
            'type': 'ir.actions.act_url',
            'name': "Shipment Tracking Page",
            'target': 'new',
            'url': self._get_tracking_link(),
        }

    def _carrier_get_tracking_link(self):
        """Build a tracking url.
        You have to implement it for your carrier.
        It's like :
            'https://the-carrier.com/?track=%s' % self.parcel_tracking
        returns:
            string (url)
        """
        _logger.warning(
            "You must implement your own method named "
            "'_mycarrier_get_tracking_link'")
        pass


class StockQuantPackageApi(models.Model):
    """ API: available methods for your own implementation

        i.e. If my carrier is TNT, then I can implement

            `def _tnt_generate_labels(self, picking):`

                res = self._generate_labels(picking)
                # is the same as super on base_delivery_carrier_label
                # but with no interference with others carriers modules

                self.do_what_you_want(res)

        Each method in this class have at least picking arg to directly
        deal with stock.picking if required by your carrier use case
    """
    _inherit = "stock.quant.package"

    @implemented_by_carrier
    def _before_call(self, picking, payload):
        pass

    @implemented_by_carrier
    def _after_call(self, picking, response):
        pass

    @implemented_by_carrier
    def _get_customs(self, picking):
        pass

    @implemented_by_carrier
    def _should_include_customs(self, picking):
        pass

    @implemented_by_carrier
    def _get_parcel(self, picking):
        pass

    @implemented_by_carrier
    def _carrier_error_handling(self, payload, response):
        pass

    @implemented_by_carrier
    def _invalid_api_input_handling(self, payload, response):
        pass

    @implemented_by_carrier
    def _prepare_label(self, label, picking):
        pass

    @implemented_by_carrier
    def _handle_attachments(self, label, response):
        pass

    @implemented_by_carrier
    def _handle_tracking(self, label, response):
        pass

    @implemented_by_carrier
    def _get_tracking_link(self):
        pass

    @implemented_by_carrier
    def _generate_labels(self, picking):
        pass

    @implemented_by_carrier
    def _get_parcels(self, picking):
        pass

    # end of API
