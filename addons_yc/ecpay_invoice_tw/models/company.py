# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ResCompany(models.Model):
    _inherit = "res.company"

    ecpay_demo_mode = fields.Boolean(string='測試模式', help='會使用測試電子發票的API網址進行開票')
    ecpay_MerchantID = fields.Char(string='MerchantID')
    ecpay_HashKey = fields.Char(string='HashKey')
    ecpay_HashIV = fields.Char(string='HashIV')
    auto_invoice = fields.Selection(string='開立電子發票方式', required=True,
        selection=[('manual', '手動'), ('automatic', '自動'), ('hand in', '人工填入')])
    seller_Identifier = fields.Char(string='賣方統編')

    