# -*- coding: utf-8 -*-

{
    'name': 'Trs',
    'version': '0.3',
    'author': 'Akretion',
    'summary': 'Trs par roulier',
    'maintainer': 'Akretion',
    'category': 'Warehouse',
    'depends': [
        'delivery_carrier_b2c',
        'delivery_carrier_label_roulier',
        'delivery_carrier_deposit',
        'attachment_metadata',
    ],
    'description': """
Delivery Carrier Trs
==========================


Description
-----------
Implementation of shipment for french carrier "TRS".

How to use:

- add TRS as delivery method of the sale order
- print the label and stick it to the cardboard box
- when the truck is loaded, create the delivery slip 
(Warehouse > Create delivery slip)
- send the delivery slip (mail or ftp)

How it works:

- Labels (.zpl) are generated offline with the package id as barcode
- Link between barcode and address is done by sending the delivery slip
to the carrier 


Known Issues / Not implemented yet
----------------------------------

Not implemented:
* Multiple package per shippment
* advanced features (number of drivers, day of delivery...)
* sending the delivery slip automatically


Contributors
------------

* Raphaël REVERDY <raphael.reverdy@akretion.com>

----

    """,
    'website': 'http://www.akretion.com/',
    'data': [
        'data/delivery.xml',
    ],
    'demo': [
    ],
    'tests': [],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
    'application': False,
}
