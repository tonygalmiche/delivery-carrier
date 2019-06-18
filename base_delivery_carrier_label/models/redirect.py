# Copyright 2019 Akretion <http://www.akretion.com>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def redirect(self, func_name, picking=None, args=None, kwargs=None):
    """
        Allow to switch to the adhoc method
    """
    delivery_type = guess_delivery_type()
    method = '_%s%s' % (delivery_type, func_name)
    if hasattr(self, method):
        return getattr(self, method)(*args, **kwargs)
    _logger.info(
        "You may implement your own method named "
        "'%s()' for your carrier" % method)
    return False


def guess_delivery_type(self):
    if self._name == 'stock.picking':
        delivery_type = self.delivery_type
    elif self._name == 'stock.quant.package':
        delivery_type = self.picking.delivery_type
    return delivery_type
