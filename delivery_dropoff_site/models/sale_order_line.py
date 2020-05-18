# Copyright 2020 Akretion France
# @author: Raphaël Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _prepare_procurement_values(self, group_id):
    	# Propagate the final_shipping_partner_id into the procurement group
        res = super()._prepare_procurement_values(group_id)
        if group_id:
            group_id.final_shipping_partner_id = self.order_id.final_shipping_partner_id
        return res
