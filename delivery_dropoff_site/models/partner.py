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

    dropoff_site = fields.Boolean(
        string='Dropoff Site',
        help="Specific areas where carriers ship merchandises and "
             "recipients comes pick their packages")
    dropoff_site_ids = fields.One2many(
        comodel_name='partner.dropoff.site',
        inverse_name='partner_id',
        string='Dropoff Sites')

    # def name_search(self, cr, uid, name='', args=None, operator='ilike',
    #                 context=None, limit=80):
    #     domain = args
    #     if domain is None:
    #         domain = []
    #     if not search_domain_key(domain, 'dropoff_site_ids'):
    #         domain.append(['dropoff_site_ids', '=', False])
    #     return super(ResPartner, self).name_search(
    #         cr, uid, name=name, args=domain, operator=operator,
    #         context=context, limit=limit)

    # _sql_constraints = [
    #     ('dropoff_site_id_uniq', 'unique(dropoff_site_id)',
    #      "Dropoff Site with the same id already exists : must be unique"),
    # ]


class AbstractDropoffSite(models.AbstractModel):
    """ For performance needs, you may insert raw dropoff datas in an sql
        temporary table. In this cases inherit of this class
    """
    _name = 'abstract.dropoff.site'
    _description = 'Common fields for dropoff tables'

    weight = fields.Float(
        string='Weight',
        help='Max weight (kg) for the site per package unit '
             '(from the viewpoint of handling)')
    subtype = fields.Char(
        string='Sub Type', index=True,
        help="Name/code to define the area : shop, postal center, etc.")
    longitude = fields.Float(string='Longitude')
    latitude = fields.Float(string='Lattitude')


class PartnerDropoffSite(models.Model):
    _name = "partner.dropoff.site"
    _description = "Partner dropoff site (delivery point)"
    _inherit = 'abstract.dropoff.site'
    _inherits = {'res.partner': 'partner_id'}
    _rec_name = 'ref'
    _dropoff_type = None

    dropoff_type = fields.Char(
        string='Type', required=True,
        help='example : UPS, Postal area, Fedex, etc.')
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner', required=True, ondelete='cascade')

    @api.multi
    def goto_partner_button(self):
        self.ensure_one()
        return {
            'name': 'Dropoff Site Partner',
            'view_mode': 'form',
            'res_id': self.partner_id.id,
            'res_model': 'res.partner',
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    @api.multi
    def name_get(self):
        res = []
        for site in self:
            address_name = site.partner_id.name_get()[0][1]
            res.append((site.id, "%s - %s" % (site.ref, address_name)))
        return res

    @api.multi
    def write(self, vals):
        return super(PartnerDropoffSite, self).write(vals)

    @api.model
    def create(self, vals):
        vals.update({
            'customer': False,
            'supplier': False,
            'dropoff_site': True,
        })
        return super(PartnerDropoffSite, self).create(vals)
