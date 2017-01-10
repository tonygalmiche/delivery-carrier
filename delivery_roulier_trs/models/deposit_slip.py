# -*- coding: utf-8 -*-

from base64 import b64encode

from openerp import models

from roulier import roulier


class DepositSlip(models.Model):
    _inherit = "deposit.slip"

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

    def _trs_create_edi_file(self, lines):
        """Create a .csv file with headers and data.

        params:
            lines : [OrderedDict]
        return: io.ByteIO
        """
        trs = roulier.get('trs')
        csv = trs.get_deposit_slip(lines)  # io.ByteIO
        return csv

    def _trs_create_attachment(self):
        """Create a slip and add it in attachment."""
        lines = self._trs_create_edi_lines()
        edi_file = self._trs_create_edi_file(lines)
        csv_name = '%s.csv' % self.name
        vals = {
            'name': csv_name,
            'res_id': self.id,
            'res_model': 'deposit.slip',
            'datas': b64encode(edi_file.getvalue()),
            'datas_fname': csv_name,
            'type': 'binary',
        }
        return self.env['ir.attachment.metadata'].create(vals)

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
        

