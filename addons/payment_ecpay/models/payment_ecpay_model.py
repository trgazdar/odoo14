# coding: utf-8

import json
import logging
import pprint
import dateutil.parser
import pytz
from werkzeug import urls
from datetime import datetime
import binascii
import collections
import json
import hashlib
import copy
from urllib.parse import quote_plus

from odoo import api, fields, models, _
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.addons.payment_ecpay.controllers.main import EcpayController
from odoo.tools.float_utils import float_compare
from odoo.http import request

from odoo.addons.payment_ecpay.controllers.ecpay_payment_sdk import *

_logger = logging.getLogger(__name__)


class AcquirerEcpay(models.Model):
    _inherit = 'payment.acquirer'
    provider = fields.Selection(selection_add=[('ecpay', 'ECPay 綠界第三方支付')], ondelete={'ecpay':'set default'})

    MerchantID = fields.Char(
        '特店編號',
        required_if_provider='ecpay',
        groups='base.group_user',
        help='特店編號')
    HashKey = fields.Char(
        '介接 HashKey',
        groups='base.group_user',
        required_if_provider='ecpay')
    HashIV = fields.Char(
        '介接 HashIV',
        groups='base.group_user',
        required_if_provider='ecpay')

    ecpay_credit = fields.Boolean(
        '信用卡一次付清', default=True,
        help='信用卡一次付清', groups='base.group_user')
    # Odoo 金流測試報告 20181228
    ecpay_credit_installment_3 = fields.Boolean(
        '信用卡分期付款(3期)', default=True,
        help='信用卡分期付款(3期)', groups='base.group_user')
    ecpay_credit_installment_6 = fields.Boolean(
        '信用卡分期付款(6期)', default=True,
        help='信用卡分期付款(6期)', groups='base.group_user')
    ecpay_credit_installment_12 = fields.Boolean(
        '信用卡分期付款(12期)', default=True,
        help='信用卡分期付款(12期)', groups='base.group_user')
    ecpay_credit_installment_18 = fields.Boolean(
        '信用卡分期付款(18期)', default=True,
        help='信用卡分期付款(18期)', groups='base.group_user')
    ecpay_credit_installment_24 = fields.Boolean(
        '信用卡分期付款(24期)', default=True,
        help='信用卡分期付款(24期)', groups='base.group_user')
    ecpay_googlepay = fields.Boolean(
        'GooglePay', default=True,
        help='GooglePay (若為 PC 版時不支援)', groups='base.group_user')
    ecpay_webatm = fields.Boolean(
        '網路 ATM', default=True,
        help='網路 ATM (若為手機版時不支援)', groups='base.group_user')
    ecpay_atm = fields.Boolean(
        '自動櫃員機 ATM', default=True,
        help='自動櫃員機 ATM', groups='base.group_user')
    ecpay_cvs = fields.Boolean(
        '超商代碼', default=True,
        help='超商代碼', groups='base.group_user')
    ecpay_barcode = fields.Boolean(
        '超商條碼', default=True,
        help='超商條碼 (若為手機版時不支援)', groups='base.group_user')
    ecpay_domain = fields.Char(
        '網域名稱',
        default='https://your_domain_name/',
        groups='base.group_user',
        required_if_provider='ecpay')

    def ecpay_form_generate_values(self, values):
        """
        將訂單資料填入表單(form), 將透過 POST 傳至綠界 URL
        (Callback fun 2)
        """
        pprint.pprint(values)
        # 檢查 values 是否有傳值進來
        # if 'SO' not in values.get('reference'):
        #     return {}
        sale_order_name = values['reference'].split('-', 1)[0]

        # 取得 ECPay 的後台設定值
        ecpay_payment_sdk = self.env['payment.transaction']._ecpay_get_sdk()

        # 取得 domain
        # Odoo 金流測試報告 20181115
        # base_url = base_url.replace('http:', 'https:', 1)
        base_url = self.ecpay_domain if self.ecpay_domain else self.env['ir.config_parameter'].sudo(
        ).get_param('web.base.url')

        # 組合商品名稱
        item_name = ""
        ecpay_tx_values = dict()
        sale_order = self.env['sale.order'].sudo().search(
            [('name', '=', sale_order_name)])
        # 如果商品名稱有多筆，需在金流選擇頁一行一行顯示商品名稱的話，商品名稱請以符號 # 分隔
        if sale_order:
            for sale_order_line in sale_order.order_line:
                sep = '\n'
                sale_order_line_name = sale_order_line.name.split(sep, 1)[0]
                item_name += sale_order_line_name + "#"
            item_name = item_name.strip('#')

        # 組合客戶付款後返回網址
        client_back_url = urls.url_join(base_url, EcpayController._return_url)
        if sale_order.access_token:
            client_back_url = urls.url_join(base_url, '/my/orders/' + str(
                sale_order.id) + '?access_token=' + str(sale_order.access_token))

        # 建立綠界需要的交易資料, 需連動到 payment_ecpay_templates.xml
        params = {
            'MerchantTradeNo': sale_order_name + 'N' + datetime.now().strftime("%m%d%H%M%S"),
            'MerchantTradeDate': datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
            'TotalAmount': int(values['amount']),
            'TradeDesc': 'ecpay_module_odoo12',
            # Odoo 金流測試報告 20181115
            'ItemName': '服飾商品一批',
            'ReturnURL': urls.url_join(base_url, EcpayController._notify_url),
            'ClientBackURL': client_back_url,
            'PaymentInfoURL': urls.url_join(base_url, EcpayController._info_notify_url),
            'ChoosePayment': request.session.get('payment_type', 'Credit'),
            'NeedExtraPaidInfo': 'Y',
            'CustomField1': values['reference'],
        }

        # 信用卡分期付款
        # Odoo 金流測試報告 20181228
        payment_type = request.session.get('payment_type')
        if payment_type and ('CreditInstallment' in payment_type):
            CreditInstallment = '3,6,12,18,24'
            if payment_type == 'CreditInstallment3':
                CreditInstallment = '3'
            elif payment_type == 'CreditInstallment6':
                CreditInstallment = '6'
            elif payment_type == 'CreditInstallment12':
                CreditInstallment = '12'
            elif payment_type == 'CreditInstallment18':
                CreditInstallment = '18'
            elif payment_type == 'CreditInstallment24':
                CreditInstallment = '24'
            params.update({
                'ChoosePayment': 'Credit',
                'CreditInstallment': CreditInstallment,
            })

        # 發送綠界訂單前, 先建立一筆訂單在資料庫
        # self.env['order.ecpay.model'].sudo().order_record(params)

        # 準備 form 資料傳給 template ecpay_form, 讓 ecpay_form 自動 summit 出去給綠界
        ecpay_tx_values['parameters'] = ecpay_payment_sdk.create_order(params)
        # pprint.pprint(ecpay_tx_values)
        return ecpay_tx_values

    @api.model
    def _get_ecpay_urls(self, environment):
        if environment == 'enabled':
            return {
                # 正式環境
                'ecpay_form_url': 'https://payment.ecpay.com.tw/Cashier/AioCheckOut/V5',
            }
        else:
            return {
                # 測試環境
                'ecpay_form_url': 'https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5',
            }

    def ecpay_get_form_action_url(self):
        """
        綠界接收表單(form)的 URL
        將訂單資料以 POST(HTTP Method) 傳送至綠界, 準備進行付款
        (Callback fun 3)
        """
        return self._get_ecpay_urls(self.state)['ecpay_form_url']


class TxEcpay(models.Model):
    _inherit = 'payment.transaction'

    ecpay_txn_type = fields.Char('Transaction type')

    @api.model
    def _ecpay_get_sdk(self):
        # 取得 ECPay 的後台設定值
        ecpay_setting = self.env['payment.acquirer'].search(
            [('provider', '=', 'ecpay')], limit=1)
        return ECPayPaymentSdk(
            MerchantID=ecpay_setting.MerchantID,
            HashKey=ecpay_setting.HashKey,
            HashIV=ecpay_setting.HashIV)

    # --------------------------------------------------
    # FORM RELATED METHODS
    # --------------------------------------------------

    @api.model
    def _ecpay_form_get_tx_from_data(self, data):
        """
        1. 收到綠界的付款結果訊息，並判斷檢查碼是否相符
        2. 特店必須檢查檢查碼 [CheckMacValue] 來驗證
        """
        # 透過 reference 去找系統有沒有這筆訂單
        reference = data.get('CustomField1')
        if not reference:
            error_msg = _(
                'Ecpay: received data with missing reference (%s)') % reference
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        tx = self.search([('reference', '=', reference)])
        if not tx or len(tx) > 1:
            error_msg = 'Ecpay: received data for reference %s' % (pprint.pformat(reference))
            if not tx:
                error_msg += '; no order found'
            else:
                error_msg += '; multiple order found'
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        _logger.info(tx)
        return tx

    def _ecpay_form_get_invalid_parameters(self, data):
        invalid_parameters = []
        return invalid_parameters

    def _ecpay_form_validate(self, data):
        """
        判斷是否交易成功, 或是交易資訊
        """
        former_tx_state = self.state
        return_code = int(data.get('RtnCode'))
        payment_type = data.get('PaymentType')
        res = {
            'acquirer_reference': data.get('CustomField1'),
            'state_message': data.get('RtnMsg'),
        }
        # 若回傳值為1時，為付款成功
        if return_code == 1:
            self._set_transaction_done()
            if self.state == 'done' and self.state != former_tx_state:
                _logger.info('Validated payment for tx %s: set as done' % (self.reference))
                return self.write(res)
        # ATM 回傳值時為 2 時，交易狀態為取號成功
        # CVS/BARCODE 回傳值時為 10100073 時，交易狀態為取號成功
        elif (('ATM' in payment_type) and (return_code == 2)) or \
            (('BARCODE' in payment_type) and (return_code == 10100073)) or \
                (('CVS' in payment_type) and (return_code == 10100073)):
            self._set_transaction_pending()
            if self.state == 'pending' and self.state != former_tx_state:
                _logger.info('Received notification for payment %s: set as pending' % (self.reference))
                return self.write(res)
        else:
            error = 'Received unrecognized status for Paypal payment %s, set as error' % (self.reference)
            res.update(state_message=error)
            self._set_transaction_cancel()
            if self.state == 'cancel' and self.state != former_tx_state:
                _logger.info(error)
                return self.write(res)
        return True

    @api.model
    def ecpay_check_mac_value(self, post):
        # 取得 ECPay 的 SDK
        ecpay_payment_sdk = self._ecpay_get_sdk()
        # 先將 CheckMacValue 取出
        CheckMacValue = post.pop('CheckMacValue')
        # 將 POST data 計算驗證是否相符
        if CheckMacValue == ecpay_payment_sdk.generate_check_value(post):
            s = self.search([('reference', '=', post.get('CustomField1', ''))], limit=1)
            return s.acquirer_id.state if any(s) else ''
        else:
            error_msg = _('Ecpay: CheckMacValue is not correct')
            _logger.info(error_msg)
            return False


class OrderEcpayModel(models.Model):
    _name = 'order.ecpay.model'

    MerchantTradeDate = fields.Char(
        '訂單日期',
        groups='base.group_user',
        help='訂單日期')
    ReferenceNo = fields.Char(
        '訂單編號',
        groups='base.group_user',
        help='訂單編號')
    MerchantTradeNo = fields.Char(
        '廠商訂單編號',
        groups='base.group_user',
        help='廠商訂單編號')
    TradeNo = fields.Char(
        '綠界金流訂單編號',
        groups='base.group_user',
        help='綠界金流訂單編號')
    PaymentType = fields.Char(
        '付款方式',
        groups='base.group_user',
        help='付款方式')
    PaymentDate = fields.Char(
        '付款日期',
        groups='base.group_user',
        help='付款日期')
    card4no = fields.Char(
        '信用卡卡號末4碼',
        groups='base.group_user',
        help='信用卡卡號末4碼')
    stage = fields.Char(
        '分期期數',
        groups='base.group_user',
        help='分期期數')
    RtnCode = fields.Char(
        '付款狀態',
        groups='base.group_user',
        help='付款狀態')
    TradeAmt = fields.Char(
        '交易金額',
        groups='base.group_user',
        help='交易金額')
    InvoiceMark = fields.Char(
        '電子發票',
        groups='base.group_user',
        help='電子發票')
    BankCode = fields.Char(
        '銀行代碼',
        groups='base.group_user',
        help='銀行代碼')
    vAccount = fields.Char(
        '虛擬帳號',
        groups='base.group_user',
        help='虛擬帳號')
    ExpireDate = fields.Char(
        '繳費期限',
        groups='base.group_user',
        help='繳費期限')
    PaymentNo = fields.Char(
        '繳費代碼',
        groups='base.group_user',
        help='繳費代碼')
    Barcode1 = fields.Char(
        '繳費條碼1',
        groups='base.group_user',
        help='繳費條碼第一段號碼')
    Barcode2 = fields.Char(
        '繳費條碼2',
        groups='base.group_user',
        help='繳費條碼第二段號碼')
    Barcode3 = fields.Char(
        '繳費條碼3',
        groups='base.group_user',
        help='繳費條碼第三段號碼')
    RtnMsg = fields.Char(
        '交易訊息',
        groups='base.group_user',
        help='交易訊息')

    sale_order_id = fields.Many2one('sale.order', '銷售訂單')

    def order_info_record(self, data):
        """
        如果是 ATM、CVS 或 BARCODE, 綠界會將資料送到 _info_notify_url
        # 先撈出 MerchantTradeNo 是否存在在此表裡面，
        # 並找出對應的付款交易單[payment.transaction]來取得對應的銷售單[sales.order]，
        # 並建立與此紀錄關聯
        """
        order = self.search(
            [('MerchantTradeNo', '=', data.get('MerchantTradeNo')), ], limit=1)

        info_data = {
            'MerchantTradeDate': data.get('TradeDate'),
            'MerchantTradeNo': data.get('MerchantTradeNo'),
            'TradeNo': data.get('TradeNo'),
            'PaymentType': data.get('PaymentType'),
            'RtnCode': data.get('RtnCode'),
            'TradeAmt': data.get('TradeAmt'),
            'BankCode': data.get('BankCode'),
            'vAccount': data.get('vAccount'),
            'ExpireDate': data.get('ExpireDate'),
            'PaymentNo': data.get('PaymentNo'),
            'Barcode1': data.get('Barcode1', ''),
            'Barcode2': data.get('Barcode2', ''),
            'Barcode3': data.get('Barcode3', ''),
            'RtnMsg': data.get('RtnMsg'),
        }

        transaction = self.env['payment.transaction'].search(
            [('reference', '=', data.get('CustomField1')), ], limit=1)

        create_data = False
        for sale_order_id in transaction.sale_order_ids:
            pattern = [(1, order.id, info_data)] if any(order) else [(0, 0, info_data)]
            sale_order_id.ecpay_info_ids = pattern
            create_data = True
        return create_data

    def order_paid_record(self, data):
        # 用此筆交易的 reference 去找尋 sale.order
        transaction = self.env['payment.transaction'].search(
            [('reference', '=', data.get('CustomField1')), ],
            limit=1
        )
        # 使用 transaction 的銷售訂單 id, 去建立銷售訂單的綠界支付資訊
        for sale_order_id in transaction.sale_order_ids:
            paid_data = {
                'MerchantTradeDate': data.get('TradeDate'),
                'MerchantTradeNo': data.get('MerchantTradeNo'),
                'PaymentDate': data.get('PaymentDate'),
                'PaymentType': data.get('PaymentType'),
                'RtnCode': data.get('RtnCode'),
                'RtnMsg': data.get('RtnMsg'),
                'TradeAmt': data.get('TradeAmt'),
                'TradeNo': data.get('TradeNo'),
                'card4no': data.get('card4no'),
                'stage': data.get('stage'),
            }
            result = sale_order_id.ecpay_info_ids = [(0, 0, paid_data)]
            print(result)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    ecpay_info_ids = fields.One2many(
        'order.ecpay.model',
        'sale_order_id',
        '綠界支付資訊'
    )