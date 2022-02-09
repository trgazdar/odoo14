# -*- coding: utf-8 -*-

{
    'name': '仿 odoo12 庫存調整',
    'summary': '在不影響現在的運作架構下可以查看庫存盤點的必要資訊',
    'version': '1.0',
    'description': """在不影響現在的運作架構下可以查看庫存盤點的必要資訊""",
    'depends': ['stock'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/view.xml',
    ],
    'qweb': [
    ],
    'installable': True,
}
