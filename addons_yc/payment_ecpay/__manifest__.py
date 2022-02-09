# -*- coding: utf-8 -*-

{
    'name': 'ECPay 綠界第三方金流模組',
    'category': 'Accounting',
    'summary': 'Payment Acquirer: ECPay 綠界第三方金流模組',
    'version': '1.0',
    'description': """ECPay 綠界第三方金流模組""",
    'author' : 'Zen Tseng',
    'depends': ['payment', 'sale', 'web'],
    'data': [
        'security/payment_ecpay_access_rule.xml',
        'security/ir.model.access.csv',
        'views/payment_views.xml',
        'views/payment_ecpay_templates.xml',
        'views/payment_ecpay_order_templates.xml',
        'views/payment_ecpay_order_views.xml',
        'data/payment_acquirer_data.xml',
    ],
    'installable': True,
    'post_init_hook': 'create_missing_journal_for_acquirers',
}
