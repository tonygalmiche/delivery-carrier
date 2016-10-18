# coding: utf-8
# © 2016 David BEAL @ Akretion <david.beal@akretion.com>
#        Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # has_final_recipient state should be changed in carrier_id_change method
    # according to choosen delivery method
    final_partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Final Recipient',
        domain=[('customer', '=', True)],
        help="It is the partner that will pick up the parcel "
             "in the dropoff site.")
    has_final_recipient = fields.Boolean(
        string='Has Final Partner', default=False,
        help='Use to facilitate display')

    @api.multi
    def _check_dropoff_site_according_to_carrier(self):
        """ carrier_id_change onchange manage partner_id domain
            but does not prevent change carrier after partner (dropoff).
            So some module could deals between them
        """
        pass

    @api.multi
    def goto_dropoff_button(self):
        self.ensure_one()
        ids = self.env['partner.dropoff.site'].search(
            [('partner_id', '=', self.partner_id.id)])
        return {
            'name': 'Dropoff Site',
            'view_mode': 'form',
            'res_id': ids[0],
            'res_model': 'partner.dropoff.site',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
        }
