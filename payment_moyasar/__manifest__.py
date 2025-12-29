# -*- coding: utf-8 -*-
{
    'name': "Moyasar Payment Gateway",
    'version': "18.0.1.0.0",
    'category': "Accounting/Payment Providers",
    'summary': "Integrate Moyasar payment gateway with Odoo 18 eCommerce and Invoicing.",
    'description': """
        Moyasar Payment Gateway Integration
        ===================================
        This module integrates the Moyasar payment gateway with Odoo 18,
        allowing customers to make secure online payments through supported
        methods such as Mada, Visa, and MasterCard.

        Key Features:
        --------------
        - Full integration with Odoo Payments and Website Sale.
        - Supports Mada, Visa, and MasterCard.
        - Inline payment form with real-time validation.
        - Automatic transaction creation and synchronization.
        """,
    'author': "Mantu Raj",
    'license': "LGPL-3",

    # Dependencies
    'depends': [
        'payment',
        'website_sale',
        'web',
    ],

    # Data files
    'data': [
        'data/payment_provider_data.xml',
        'views/payment_provider_views.xml',
        'views/payment_templates.xml',
    ],

    # Assets
    'assets': {
        'web.assets_frontend': [
            'payment_moyasar/static/src/js/moyasar_min.js',
            'payment_moyasar/static/src/js/payment_moyasar.js',
        ],
        'web.assets_qweb': [
            'payment_moyasar/static/src/xml/payment_moyasar_templates.xml',
        ],
    },

    # Technical info
    'installable': True,
    'application': False,
    'auto_install': False,
}
