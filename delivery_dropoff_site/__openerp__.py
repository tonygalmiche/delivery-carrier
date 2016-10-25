# coding: utf-8
# © 2016 David BEAL @ Akretion <david.beal@akretion.com>
#        Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Delivery Drop-off Site',
    'version': '8.0.0.0.1',
    'author': 'Akretion',
    'summary': "Send goods to sites in which customers come pick up package",
    'maintener': 'Akretion',
    'category': 'Warehouse',
    'depends': [
        'base_delivery_carrier_label',
        'sale',
    ],
    'description': """
Delivery Drop-off Site
======================

Manage features related to drop-off sites
-----------------------------------------

Main international carriers provide transportation services to specific areas
managed by them or by subcontractors.

Then, recipients come pick up their packages in these sites.


Contributors
------------

* David BEAL <david.beal@akretion.com>
* Sébastien BEAU <sebastien.beau@akretion.com>

""",
    'website': 'http://www.akretion.com/',
    'data': [
        'data/delivery_data.xml',
        'views/stock_view.xml',
        'views/partner_view.xml',
        'views/sale_view.xml',
    ],
    'demo': [
        'demo/demo.xml',
        'demo/partner.dropoff.site.csv',
    ],
    'license': 'AGPL-3',
    'installable': True,
}
