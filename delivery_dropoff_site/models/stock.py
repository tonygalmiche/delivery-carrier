# coding: utf-8
# © 2016 David BEAL @ Akretion <david.beal@akretion.com>
#        Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, api, models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

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

    @api.onchange('final_partner_id')
    def onchange_final_partner_id(self):
        if self.final_partner_id:
            return {
                'domain': {'partner_id': [
                    ('dropoff_site_type', '=', self.carrier_type),
                    ('dropoff_site', '=', True),
                ]}}

    @api.multi
    @api.depends('option_ids')
    def _compute_final_recipient(self):
        dropoff_site_opt = self.env.ref(
            'delivery_dropoff_site.'
            'delivery_carr_tmpl_to_dropoff', False)
        if not dropoff_site_opt:
            # At install process this xml data is not
            # there, so has_final_recipient field can't be computed.
            # No problem only useful for new data.
            return
        for rec in self:
            if dropoff_site_opt in [x.tmpl_option_id for x in rec.option_ids]:
                rec.has_final_recipient = True
                rec.final_partner_id = rec.partner_id
                rec.partner_id = False
            else:
                rec.has_final_recipient = False
                if rec.final_partner_id:
                    rec.partner_id = rec.final_partner_id

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
        action = {
            'name': _('Dropoff Site %s' % self.carrier_type),
            'view_mode': 'tree,form',
            'res_model': 'partner.dropoff.site',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': {'default_dropoff_type': self.carrier_type},
        }
        dropoffs = self.env['partner.dropoff.site'].search(
            [('dropoff_type', '=', self.carrier_type)])
        if dropoffs:
            dropoff_ids = [x.id for x in dropoffs]
            action['domain'] = [('id', 'in', dropoff_ids), ]
        return action
