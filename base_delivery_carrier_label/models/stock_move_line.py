# Copyright 2016 Hpar
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
from collections import defaultdict

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    weight = fields.Float(
        digits=dp.get_precision('Stock Weight'),
        help="Weight of the pack_operation"
    )

    @api.multi
    def get_weight(self):
        """Calc and save weight of pack.operations.

        Warning: Type conversion not implemented
                it will return False if at least one uom or uos not in kg
        return:
            the sum of the weight of [self]
        """
        total_weight = 0
        kg = self.env.ref('uom.product_uom_kgm').id
        units = self.env.ref('uom.product_uom_unit').id
        allowed = (False, kg, units)
        cant_calc_total = False
        for operation in self:
            product = operation.product_id

            # if not defined we assume it's in kg
            if product.uom_id.id not in allowed:
                _logger.warning(
                    'Type conversion not implemented for product %s' %
                    product.id)
                cant_calc_total = True

            operation.weight = (product.weight * operation.product_qty)

            total_weight += operation.weight

        if cant_calc_total:
            return False
        return total_weight

    @api.model
    def _update_picking_package(self, package_ids):
        packages = self.env['stock.quant.package'].browse(package_ids)
        pack_pick = packages._get_pickings_from_packages()
        for pack in packages:
            if not pack_pick.get(pack.id):
                ''

    @api.model
    def create(self, vals):
        res = super().create(vals)
        package_ids = [vals.get('package_id'), vals.get('result_package_id')]
        self._update_picking_package(package_ids)
        return res

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        package_ids = []
        for rec in self:
            package_ids.append(rec.package_id.id or vals.get('package_id'))
            package_ids.append(rec.result_package_id.id or vals.get(
                'result_package_id'))
        self._update_picking_package(self, package_ids)
        return res

    @api.multi
    def unlink(self):
        package_ids = [x.result_package_id or x.package_id for x in self]
        res = super().write()
        self._update_picking_package(package_ids)
        return res


class StockQuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    @api.multi
    def _get_pickings_from_packages(self):
        """ Get all pickings from package """
        mapping = defaultdict(list)
        move_lines = self.env['stock.move.line'].search(
            ['|',
             ('package_id', 'in', self.ids),
             ('result_package_id', 'in', self.ids),
             ('picking_id.picking_type_id.code', '=', 'outgoing')])
        for line in move_lines:
            mapping[line.result_package_id or line.package_id].append(
                line.picking_id)
        return mapping
