# coding: utf-8
# © 2016 Raphael REVERDY <raphael.reverdy@akretion.com>
#        David BEAL <david.beal@akretion.com>
#        Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Delivery Carrier La Poste (fr)',
    'version': '9.0.1.0.0',
    'author': 'Akretion',
    'summary': 'Generate Label for La Poste/Colissimo',
    'maintainer': 'Akretion,Odoo Community Association (OCA)',
    'category': 'Warehouse',
    'depends': [
        'delivery_roulier',
        'delivery_roulier_options',
        'intrastat_base',  # for customs declaration
    ],
    'website': 'http://www.akretion.com/',
    'data': [
        'data/delivery.xml',
    ],
    'external_dependencies': {
        'python': [
            'roulier',
        ]
    },
    'installable': True,
    'license': 'AGPL-3',
}
