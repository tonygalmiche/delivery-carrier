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

    @api.depends('dropoff_site_id')
    def _compute_dropoff_site(self):
        res = {}
        for elm in self:
            dropoff = self.env['partner.dropoff.site'].search(
                [('partner_id', '=', elm.id)])
            res[elm.id] = False
            if dropoff:
                res[elm.id] = dropoff[0]
        return res

    @api.multi
    def write(self, vals):
        if 'partner_id' in vals:
            self._store_set_values(['dropoff_site_id'])
        return super(ResPartner, self).write(vals)

    # def _get_partner_ids_from_dropoffsite(self, cr, uid, ids, context=None):
    #     partner_ids = []
    #     for dropoff in self.browse(cr, uid, ids, context=context):
    #         partner_ids.append(dropoff.partner_id.id)
    #     return partner_ids

    dropoff_site_id = fields.Many2one(
        comodel_name='partner.dropoff.site',
        string='Dropoff Site',
        compute='_compute_dropoff_site', store=True,
        help="... are specific areas where carriers ship merchandises.\n"
             "Recipients comes pick up their parcels in these sites",)

    def name_search(self, cr, uid, name='', args=None, operator='ilike',
                    context=None, limit=80):
        domain = args
        if domain is None:
            domain = []
        if not search_domain_key(domain, 'dropoff_site_id'):
            domain.append(['dropoff_site_id', '=', False])
        return super(ResPartner, self).name_search(
            cr, uid, name=name, args=domain, operator=operator,
            context=context, limit=limit)

    _sql_constraints = [
        ('dropoff_site_id_uniq', 'unique(dropoff_site_id)',
         "Dropoff Site with the same id already exists : must be unique"),
    ]


class AbstractDropoffSite(models.AbstractModel):
    """ For performance needs, you may insert raw dropoff datas in an sql
        temporary table. In this cases inherit of this class
    """
    _name = 'abstract.dropoff.site'
    _description = 'Common fields for dropoff tables'

    code = fields.Char(
        string='Dropoff Site Code',
        help='Code of the site in carrier infmodelsation system')
    weight = fields.Float(
        'Weight',
        help='Max weight (kg) for the site per package unit '
        '(from the viewpoint of handling)')
    subtype = fields.Char(
        'Sub Type',
        index=True,
        help="Name/code to define the area : shop, postal center, etc.")
    longitude = fields.Float(string='Longitude')
    latitude = fields.Float(string='Lattitude')


class PartnerDropoffSite(models.Model):
    _name = "partner.dropoff.site"
    _description = "Partner dropoff site (delivery point)"
    _inherit = 'abstract.dropoff.site'
    _inherits = {'res.partner': 'partner_id'}
    _rec_name = 'code'
    _dropoff_type = None

    dropoff_type = fields.Char(
        string='Dropoff Type',
        required=True,
        help='example : UPS, Postal area, Fedex, etc.')
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner', required=True, ondelete='cascade')

    @api.multi
    def name_get(self):
        res = []
        for site in self:
            address_name = site.partner_id.name_get()[0][1]
            res.append((site.id, "%s - %s" % (site.code, address_name)))
        return res

    @api.model
    def create(self, vals):
        vals.update({
            'customer': False,
            'supplier': False,
        })
        return super(PartnerDropoffSite, self).create(vals)
