# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author Raphael REVERDY <raphael.reverdy@akretion.com>
#
##############################################################################

from openerp import api
from openerp.osv import orm
from base64 import b64encode
from roulier import roulier
import itertools


class DepositSlip(orm.Model):
    _inherit = "deposit.slip"

    @api.multi
    def _trs_create_edi_lines(self):
        """Create lines for each picking.

        The carrier is expecting a line per shipping.
        @returns []
        """
        self.ensure_one()
        lines = []
        for picking in self.picking_ids:
            lines += picking.trs_get_meta()
        return lines

    @api.multi
    def _trs_create_edi_file(self, lines):
        """Create a .csv file with headers and data.

        params:
            lines : [OrderedDict]
        return: io.ByteIO
        """
        trs = roulier.get('trs')
        csv = trs.get_deposit_slip(lines)  # io.ByteIO
        return csv

    @api.multi
    def _trs_create_attachment(self):
        """Create a slip and add it in attachment."""
        lines = self._trs_create_edi_lines()
        edi_file = self._trs_create_edi_file(lines)
        vals = {
            'name': self.name,
            'res_id': self.id,
            'res_model': 'deposit.slip',
            'datas': b64encode(edi_file.getvalue()),
            'datas_fname': '%s.csv' % self.name,
            'type': 'binary',
        }
        return self.env['ir.attachment.metadata'].create(vals)

    @api.multi
    def create_edi_file(self):
        self.ensure_one()
        if self.carrier_type == 'trs':
            return self._trs_create_attachment()
        else:
            return super(DepositSlip, self).create_edi_file()

    # @api.multi
    # def trs_create_task(self):
    #     def get_task(self):
    #         company_id = self.picking_ids[0].company_id
    #         task = company_id.trs_repo_task_id
    #         if not task:
    #             raise UserError(
    #                 _("Carrier task"),
    #                 _("You must define a task for EDI in "
    #                 "Settings > Configuration > Carrier > TRS"))
    #             )
    #         return {
    #             "task_id": task._model._name + ','+ str(task.id),
    #             "repository_id": task.repository_id.id,
    #         }
    #     
    #     vals2 = {
    #         'active': True,
    #         'repository_id': repository_id,
    #         'direction': 'ouput',
    #         'task_id': task_id,
    #         'attachment': ''
    #     }
    #
    #    task_id, repository_id = get_task()
        

