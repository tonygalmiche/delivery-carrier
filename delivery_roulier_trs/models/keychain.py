# -*- coding: utf-8 -*-
# @author Raphael Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from openerp import models, fields

_logger = logging.getLogger(__name__)


class AccountProduct(models.Model):
    _inherit = 'keychain.account'

    namespace = fields.Selection(
        selection_add=[('roulier_trs', 'Trs')])

    def _roulier_trs_init_data(self):
        return {}

    def _roulier_trs_validate_data(self, data):
        return True
