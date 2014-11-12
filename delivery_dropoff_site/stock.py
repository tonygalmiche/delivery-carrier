# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author David BEAL <david.beal@akretion.com>
#
##############################################################################

from openerp.osv import orm, fields


class StockPicking(orm.Model):
    _inherit = 'stock.picking'

    # has_final_recipient state should be changed in carrier_id_change method
    # according to choosen delivery method
    _columns = {
        'final_partner_id': fields.many2one(
            'res.partner',
            'Final Recipient',
            domain=[('customer', '=', True)],
            help="It is the partner that will pick up the parcel "
                 "in the dropoff site."),
        'has_final_recipient': fields.boolean(
            'Has Final Partner',
            help='Use to facilitate display'),
    }

    _defaults = {
        'has_final_recipient': False,
    }

    def _check_dropoff_site_according_to_carrier(
            self, cr, uid, ids, context=None):
        """ carrier_id_change onchange manage partner_id domain
            but does not prevent change carrier after partner (dropoff).
            So some module could deals between them
        """
        return True


class StockPickingOut(orm.Model):
    _inherit = 'stock.picking.out'

    _columns = {
        'final_partner_id': fields.many2one(
            'res.partner',
            'Final Recipient',
            help="It is the partner that will pick up the parcel "
                 "in the dropoff site."),
        'has_final_recipient': fields.boolean(
            'Has Final Partner',
            help='Use to facilitate display'),
    }

    def goto_dropoff_button(self, cr, uid, ids, context=None):
        pick = self.browse(cr, uid, ids, context=context)[0]
        ids = self.pool['partner.dropoff.site'].search(
            cr, uid, [('partner_id', '=', pick.partner_id.id)], context=context)
        return {
            'name': 'Dropoff Site',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': ids[0],
            'res_model': 'partner.dropoff.site',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
        }
