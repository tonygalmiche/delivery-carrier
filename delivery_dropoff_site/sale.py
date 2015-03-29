# -*- coding: utf-8 -*-
###############################################################################
#
#   Module for OpenERP
#   Copyright (C) 2014 Akretion (http://www.akretion.com).
#   @author Sébastien BEAU <sebastien.beau@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################


from openerp.osv import fields, orm


class SaleOrder(orm.Model):
    _inherit = "sale.order"

    _columns = {
        'final_partner_id': fields.many2one(
             'res.partner',
             'Final Recipient',
             help="It is the partner that will pick up the parcel "
                  "in the dropoff site."),
    }

    def _prepare_order_picking(self, cr, uid, order, context=None):
        res = super(SaleOrder, self)._prepare_order_picking(
            cr, uid, order, context=context)
        if order.final_partner_id.id:
            res.update({
                'final_partner_id': order.final_partner_id.id,
                'has_final_recipient': True,
                })
        return res
