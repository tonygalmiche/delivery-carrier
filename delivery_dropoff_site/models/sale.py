# coding: utf-8
# © 2016 David BEAL @ Akretion <david.beal@akretion.com>
#        Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    final_partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Final Recipient',
        help="It is the partner that will pick up the parcel "
             "in the dropoff site.")

    @api.model
    def _prepare_order_picking(self, order):
        res = super(SaleOrder, self)._prepare_order_picking(order)
        if order.final_partner_id.id:
            res.update({
                'final_partner_id': order.final_partner_id.id,
                'has_final_recipient': True,
                })
        return res
