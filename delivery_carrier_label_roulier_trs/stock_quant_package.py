# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2016 Akretion (https://www.akretion.com).
#  @author Raphael Reverdy <raphael.reverdy@akretion.com>
#          David BEAL <david.beal@akretion.com>
#          Sébastien BEAU
##############################################################################

from openerp import models, fields, api
import simplejson
from collections import OrderedDict


class StockQuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    trs_meta = fields.Char(
        "meta",
        help="Needed for deposit slip (json OrderedDict)",
    )

    @api.multi
    def trs_get_meta(self):
        return (
            [OrderedDict(simplejson.loads(pack.trs_meta))
                for pack in self]
        )
