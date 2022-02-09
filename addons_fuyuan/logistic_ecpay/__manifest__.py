# -*- coding: utf-8 -*-

{
    'name': 'ECPay 綠界第三方物流模組',
    'category': 'Stock',
    'summary': '物流 (Logistic): ECPay 綠界第三方物流模組',
    'version': '14.1.3',
    'description': """ECPay 綠界物流模組""",
    'depends': ['delivery', 'website_sale_delivery', 'mail'],
    'data': [
        'security/logistic_ecpay_access_rule.xml',
        'security/ir.model.access.csv',
        'data/logistic_ecpay_data.xml',
        'views/logistic_ecpay_templates.xml',
        'views/logistic_ecpay_view.xml',
    ],
    'qweb': [
        'static/src/xml/print_cvs.xml',
    ],
    'installable': True,
    'auto_install': False,
}
