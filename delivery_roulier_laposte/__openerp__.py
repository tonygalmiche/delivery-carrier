# coding: utf-8
# © 2016 Raphael REVERDY <raphael.reverdy@akretion.com>
#        David BEAL <david.beal@akretion.com>
#        Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Delivery Carrier La Poste (fr)',
    'version': '8.0.1.0.0',
    'author': 'Akretion',
    'summary': 'Generate Label for La Poste Colissimo',
    'maintainer': 'Akretion',
    'category': 'Warehouse',
    'depends': [
        'delivery_roulier',
        'delivery_carrier_deposit',
    ],
    'description': """
Delivery Carrier ColiPoste
==========================


Description
-----------

Company:
~~~~~~~~~~
Some informations have to be filled on two locations :

* company form (Settings > Companies > Companies):
complete address of the company, included phone

* config<uration form (Settings > Configuration > Carriers > ColiPoste) :
the default test account number is 964744



Technical references
--------------------

`ColiPoste documentation`_

.. _documentation: https://www.coliposte.net

Contributors
------------

* David BEAL <david.beal@akretion.com>
* Benoit GUILLOT <benoit.guillot@akretion.com> (EDI part)
* Sébastien BEAU <sebastien.beau@akretion.com>
* Raphaël REVERDY <raphael.reverdy@akretion.com>

----

    """,
    'website': 'http://www.akretion.com/',
    'data': [
        'data/delivery.xml',
        'views/config_view.xml',
        'views/stock_view.xml',
    ],
    'demo': [
        'demo/res.partner.csv',
        'demo/company.xml',
        'demo/product.xml',
        'demo/stock.picking.csv',
        'demo/stock.move.csv',
    ],
    'installable': True,
    'license': 'AGPL-3',
}
