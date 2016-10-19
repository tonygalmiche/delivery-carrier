# coding: utf-8
# © 2016 David BEAL @ Akretion <david.beal@akretion.com>
#        Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, api, models, fields
from openerp.exceptions import Warning as UserError


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
        string='Has Final Partner', store=True,
        compute='_compute_final_recipient',
        help='Use to facilitate display')

    @api.multi
    @api.depends('option_ids')
    def _compute_final_recipient(self):
        for rec in self:
            dropoff_site_opt = self.env.ref(
                'delivery_dropoff_site.'
                'delivery_carrier_template_to_dropoff_site')
            if dropoff_site_opt in [x.tmpl_option_id for x in rec.option_ids]:
                rec.has_final_recipient = True
                rec.final_partner_id = rec.partner_id
            else:
                rec.has_final_recipient = False

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
        if ids:
            return {
                'name': 'Dropoff Site',
                'view_mode': 'form',
                'res_id': ids[0],
                'res_model': 'partner.dropoff.site',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'current',
            }
        raise UserError(_(
            "There is no Dropoff Site for this partner. "
            "Create it one first to access data."))
