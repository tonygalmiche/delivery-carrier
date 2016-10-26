# coding: utf-8
# © 2016 David BEAL <david.beal@akretion.com>
#        Raphael REVERDY <raphael.reverdy@akretion.com>
#        Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Delivery La Poste - Point Retrait',
    'version': '8.0.1.0.0',
    'author': 'Akretion',
    'summary': "Generate Label for La Poste Colissimo - Points retrait",
    'maintainer': 'Akretion',
    'category': 'Warehouse',
    'depends': [
        'delivery_roulier_laposte',
        'delivery_carrier_b2c',
        'delivery_dropoff_site',
    ],
    'description': """
Carrier label So Colissimo
==========================

Description
-----------

* Manage So Colissimo labels and reports generation
for 'ColiPoste - La Poste - FR'

* Add new delivery methods and zpl reports

So Colissimo specific :
~~~~~~~~~~~~~~~~~~~~~~~

* A2P : commerce de proximité
* CIT : Cityssimo

* CDI : Centre de distribution de la poste
* ACP : Agence Coliposte
* BPR : Bureau de poste


Contributors
------------

* David BEAL <david.beal@akretion.com>
* Sébastien BEAU <sebastien.beau@akretion.com>
* Raphael REVERDY <raphael.reverdy@akretion.com>

    """,
    'website': 'https://www.akretion.com/',
    'data': [
        'data/delivery.xml',
        'views/partner_view.xml',
    ],
    'demo': [
        'demo/partner.dropoff.site.csv',
    ],
    'installable': True,
    'license': 'AGPL-3',
}
