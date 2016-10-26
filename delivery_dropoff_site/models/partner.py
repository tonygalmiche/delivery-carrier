# coding: utf-8
# © 2016 David BEAL @ Akretion <david.beal@akretion.com>
#        Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, fields


def search_domain_key(domain, key):
    "Search 'key' in the first element of each tuple of the 'domain' list"
    for condition in domain:
        if condition[0] == key:
            return True
    return False


class ResPartner(models.Model):
    _inherit = "res.partner"

    weight = fields.Float(
        string='Weight',
        help='Max weight (kg) for the site per package unit')
    dropoff_site = fields.Boolean(
        string='Dropoff Site',
        help="Specific areas where carriers ship merchandises and "
             "recipients comes pick their packages")
    dropoff_type = fields.Char(
        string='Dropoff Type', required=True,
        help='example : UPS, Postal area, Fedex, etc.')
    dropoff_subtype = fields.Char(
        string='Sub Type', index=True,
        help="Name/code to define the area : shop, postal center, etc.")
    dropoff_code = fields.Char(
        string='Code', related='ref',
        help="Same field than 'Reference' field")

    # def name_search(self, cr, uid, name='', args=None, operator='ilike',
    #                 context=None, limit=80):
    #     domain = args
    #     print '  >>>>', context, domain
    #     # import pdb; pdb.set_trace()
    #     if domain is None:
    #         domain = []
    #     if not search_domain_key(domain, 'dropoff_site'):
    #         domain.append(['dropoff_site', '=', False])
    #     return super(ResPartner, self).name_search(
    #         cr, uid, name=name, args=domain, operator=operator,
    #         context=context, limit=limit)

    _sql_constraints = [
        ('dropoff_site_id_uniq', 'unique(dropoff_site,ref,dropoff_type)',
         "Partner Dropoff Site with the same Dropoff type and the same "
         "Reference already exists : must be unique"),
    ]
