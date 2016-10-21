# -*- coding: utf-8 -*-

{
    'name': 'Kuehne Nagel',
    'version': '0.3',
    'author': 'Akretion',
    'summary': 'Ship with Kuehne & Nagel carrier',
    'maintainer': 'Akretion',
    'category': 'Warehouse',
    'depends': [
        'delivery_carrier_b2c',
        'delivery_carrier_label_roulier',
        'delivery_carrier_deposit',
        'external_file_location',
    ],
    'description': """
Delivery Carrier Kuehne Nagel
=============================


Description
-----------

Company:
~~~~~~~~~~
Some informations have to be filled on two locations :

* company form (Settings > Companies > Companies):
complete address of the company, included phone



Technical references
--------------------

Contributors
------------

* Benoit GUILLOT <benoit.guillot@akretion.com>

----

    """,
    'website': 'http://www.akretion.com/',
    'data': [
        'data/external_file.xml',
        'views/config_view.xml',
        'views/stock_view.xml',
    ],
    'demo': [
        #   'demo/res.partner.csv',
        #   'demo/company.xml',
        #   'demo/product.xml',
    ],
    'tests': [],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
    'application': False,
}
