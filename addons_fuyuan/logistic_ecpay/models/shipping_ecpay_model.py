# coding: utf-8
import logging
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from odoo.addons.logistic_ecpay.controllers.ecpay_logistic_sdk import ECPayLogisticSdk, ECPayURL, ECPayTestURL

_logger = logging.getLogger(__name__)


class ShippingEcpayModel(models.Model):
    _name = 'shipping.ecpay.model'
    _order = 'id desc'

    name = fields.Char(
        '綠界物流訂單名稱')
    ReferenceNo = fields.Many2one('sale.order', string='訂單編號', groups='base.group_user', help='訂單編號')
    MerchantTradeNo = fields.Char(
        '廠商交易編號', groups='base.group_user', help='廠商交易編號')
    RtnCode = fields.Char('目前物流狀態', groups='base.group_user', help='目前物流狀態')
    RtnMsg = fields.Char('物流狀態說明', groups='base.group_user', help='物流狀態說明')
    AllPayLogisticsID = fields.Char(
        '綠界物流交易編號', groups='base.group_user', help='綠界物流交易編號')
    LogisticsType = fields.Char('物流類型', groups='base.group_user', help='物流類型')
    LogisticsSubType = fields.Char(
        '物流子類型', groups='base.group_user', help='物流子類型')
    GoodsAmount = fields.Char('商品金額', groups='base.group_user', help='商品金額')
    UpdateStatusDate = fields.Char(
        '物流狀態更新時間', groups='base.group_user', help='物流狀態更新時間')
    ReceiverName = fields.Char('收件人姓名', groups='base.group_user', help='收件人姓名')
    ReceiverCellPhone = fields.Char(
        '收件人手機', groups='base.group_user', help='收件人手機')
    ReceiverZipCode = fields.Char(
        '收件人郵遞區號', groups='base.group_user', help='收件人郵遞區號')
    ReceiverAddress = fields.Char(
        '收件人地址', groups='base.group_user', help='收件人地址')
    CVSPaymentNo = fields.Char('寄貨編號', groups='base.group_user', help='寄貨編號')
    CVSValidationNo = fields.Char('驗證碼', groups='base.group_user', help='驗證碼')
    BookingNote = fields.Char('托運單號', groups='base.group_user', help='托運單號')
    CVSStoreID = fields.Char('店舖編號', groups='base.group_user', help='店舖編號')
    CVSStoreName = fields.Char('店舖名稱', groups='base.group_user', help='店舖名稱')

    def name_get(self):
        return [(r.id, f"{r.ReferenceNo.name}-{r.AllPayLogisticsID}") for r in self]

    def shipping_ecpay_model_record(self, data=dict()):
        # 建立物流紀錄
        shipping_data = dict()
        shipping_data.update(data)
        # 更新 sale.order id
        reference_no = data.get('ReferenceNo')
        sale_order = self.env['sale.order'].sudo().browse(reference_no)

        if sale_order:
            shipping_data.update({'ReferenceNo': sale_order.id})

        # 查詢是否有已存在紀錄
        shipping = self.search([('ReferenceNo', '=', sale_order.id)])

        return shipping.write(shipping_data) if any(shipping) else self.create(shipping_data)

    def shipping_ecpay_model_update(self, data=dict()):
        MerchantTradeNo = data.get('MerchantTradeNo')
        # 先撈出 MerchantTradeNo 是否在資料庫裏面
        if MerchantTradeNo:
            shipping = self.search([('MerchantTradeNo', '=', MerchantTradeNo)])
            if shipping:
                # 寫入已存在紀錄
                return shipping.write(data)

    @api.model
    def get_ecpay_urls(self, environment):
        return ECPayURL if environment is True else ECPayTestURL

    def ecpay_get_form_action_url(self, cvs_type):
        # 取得 ECPay 的後台設定值
        if any(self):
            ecpay_setting = self.ReferenceNo.carrier_id
        else:
            ecpay_setting = self.env['delivery.carrier'].search(
                [('delivery_type', '=', 'ecpay')], limit=1)

        return self.get_ecpay_urls(ecpay_setting.prod_environment)[cvs_type]

    @api.model
    def _ecpay_get_sdk(self):
        # 取得 ECPay 的後台設定值
        if any(self):
            ecpay_setting = self.ReferenceNo.carrier_id
        else:
            ecpay_setting = self.env['delivery.carrier'].search([
                ('delivery_type', '=', 'ecpay')
            ], limit=1)

        return ECPayLogisticSdk(
            MerchantID=ecpay_setting.MerchantID,
            HashKey=ecpay_setting.HashKey,
            HashIV=ecpay_setting.HashIV)

    @api.model
    def print_c2c_logistic(self, model_id=0):
        # 取得指定的物流訂單，並重新定義 self
        self = self.browse(model_id)
        if not any(self):
            return '<h1>Not given any order id</h1>'
        elif self.AllPayLogisticsID == 'Wait delivery confirm':
            raise UserError('請先進行交貨確認')

        # 取得其交易方式
        delivery_carrier = self.ReferenceNo.carrier_id
        if not any(delivery_carrier):
            raise UserError('此筆訂單無設定交貨方式')

        # 取得 ECPay 的後台設定值
        ecpay_type = delivery_carrier.ecpay_type if any(delivery_carrier) else ''
        logistics_type = self.LogisticsType.lower() if self.LogisticsType else ''

        # 取得 ECPay 的 SDK
        ecpay_logistic_sdk = self._ecpay_get_sdk()
        print_c2c_bill_params = {
            'AllPayLogisticsID': self.AllPayLogisticsID,
            'PlatformID': '',
        }

        if logistics_type == 'cvs' and ecpay_type == 'c2c':
            subtype = self.LogisticsSubType
            # 統一超商
            if subtype == 'UNIMARTC2C':
                action_url = self.ecpay_get_form_action_url('PRINT_UNIMART_C2C_BILL')
                if len(self.CVSPaymentNo) < 12:
                    print_c2c_bill_params.update({
                        'CVSPaymentNo': self.CVSPaymentNo,
                        'CVSValidationNo': self.CVSValidationNo
                    })
                else:
                    print_c2c_bill_params.update({
                        'CVSPaymentNo': self.CVSPaymentNo[:len(self.CVSPaymentNo) - 4],
                        'CVSValidationNo': self.CVSPaymentNo[len(self.CVSPaymentNo) - 4:]
                    })

                final_params = ecpay_logistic_sdk.print_unimart_c2c_bill(
                    action_url=action_url,
                    client_parameters=print_c2c_bill_params)
            # 全家
            elif subtype == 'FAMIC2C':
                action_url = self.ecpay_get_form_action_url('PRINT_FAMILY_C2C_BILL')
                print_c2c_bill_params.update({
                    'CVSPaymentNo': self.CVSPaymentNo,
                })

                final_params = ecpay_logistic_sdk.print_family_c2c_bill(
                    action_url=action_url,
                    client_parameters=print_c2c_bill_params)
            # 萊爾富
            elif subtype == 'HILIFEC2C':
                action_url = self.ecpay_get_form_action_url('PRINT_HILIFE_C2C_BILL')
                print_c2c_bill_params.update({
                    'CVSPaymentNo': self.CVSPaymentNo,
                })

                final_params = ecpay_logistic_sdk.print_hilife_c2c_bill(
                    action_url=action_url,
                    client_parameters=print_c2c_bill_params)
            else:
                return f"<h1>LogisticsSubType is wrong! (subtype:{subtype})</h1>"

        elif logistics_type == 'home' or (logistics_type == 'cvs' and ecpay_type == 'b2c'):
            action_url = self.ecpay_get_form_action_url('PRINT_TRADE_DOC')
            final_params = ecpay_logistic_sdk.print_trade_doc(
                action_url=action_url,
                client_parameters=print_c2c_bill_params)
        else:
            return f"<h1>無法對應的交貨方式(id:{model_id}, carrier:{ecpay_type}, type:{logistics_type})</h1>"

        hidden_field = [f'<input type="hidden" name="{key}" value="{value}">' for key, value in
                        final_params.items()]
        return f"""
            <form id="ecpay_print" action="{action_url}" method="POST">
                {''.join(hidden_field)}
            </form
        """

    @api.model
    def ecpay_check_mac_value(self, post):
        # 取得 ECPay 的 SDK
        ecpay_logistic_sdk = self._ecpay_get_sdk()
        # 先將 CheckMacValue 取出
        check_mac_value = post.pop('CheckMacValue')
        # 將 POST data 計算驗證是否相符
        if check_mac_value == ecpay_logistic_sdk.generate_check_value(post):
            return True
        else:
            error_msg = _('Ecpay: CheckMacValue is not correct')
            _logger.info(error_msg)
            return False

class LogisticEcpaySenderInfo(models.Model):
    _inherit = 'res.company'

    SenderName = fields.Char('寄件人姓名', groups='base.group_user', help='寄件人姓名')
    SenderPhone = fields.Char('寄件人電話', groups='base.group_user', help='寄件人電話')
    SenderCellPhone = fields.Char(
        '寄件人手機', groups='base.group_user', help='寄件人手機')
    SenderZipCode = fields.Char(
        '寄件人郵遞區號', groups='base.group_user', help='寄件人郵遞區號')
    SenderAddress = fields.Char(
        '寄件人地址', groups='base.group_user', help='寄件人地址')

    @api.constrains('SenderName')
    def _onchange_sender_name(self):
        chars = set(' !@#$%^&*()_+\-=[]{};\':\"\\|,.<>\/?')
        if any((c in chars) for c in self.SenderName):
            raise ValidationError("寄件人姓名不可以有符號!")

        length = len(self.SenderName)
        utf8_length = len(self.SenderName.encode('utf-8'))
        length = (utf8_length - length) / 2 + length
        if length < 4 or length > 10:
            raise ValidationError("寄件人姓名應限制 10 字元 (最多 5 個中文、10 個英文)")

        return True

    @api.constrains('SenderPhone')
    def _onchange_sender_phone(self):
        chars = set('1234567890()-#')
        if any((c not in chars) for c in self.SenderPhone):
            raise ValidationError("寄件人電話只允許數字 + 特殊符號；特殊符號僅限()-#")

        return True

    @api.constrains('SenderCellPhone')
    def _onchange_sender_cellphone(self):
        chars = set('1234567890')
        if any((c not in chars) for c in self.SenderCellPhone) \
                or (len(self.SenderCellPhone) != 10) \
                or self.SenderCellPhone[0:2] != '09':
            raise ValidationError("寄件人手機只允許數字、10碼、09開頭")

        return True

class SaleOrder(models.Model):
    _inherit = "sale.order"

    ecpay_Logistics_id = fields.Many2one(
        'shipping.ecpay.model',
        string='綠界物流訂單編號',
        help='綠界物流訂單編號')

    def write(self, vals):
        update_complete = super(SaleOrder, self).write(vals)
        """當訂單送出時才產生綠界物流訂單"""
        if self.state in ['sent', 'sale'] and update_complete:
            carrier = self.carrier_id
            if not carrier:
                _logger.info(f'銷售訂單: {self.name}，無設定寄送方式')
                return self

            if carrier.delivery_type == 'ecpay':
                c2c = 'C2C' if carrier.ecpay_type == 'c2c' else ''
                if carrier.ecpay_unimart:
                    _type, _sub_type = 'CVS', f'UNIMART{c2c}'
                elif carrier.ecpay_fami:
                    _type, _sub_type = 'CVS', f'FAMI{c2c}'
                elif carrier.ecpay_hilife:
                    _type, _sub_type = 'CVS', f'HILIFE{c2c}'
                elif carrier.ecpay_tcat:
                    _type, _sub_type = 'HOME', 'TCAT'
                else:
                    _type, _sub_type = 'HOME', 'ECAN'

                data_set = {
                    'LogisticsType': _type,
                    'LogisticsSubType': _sub_type,
                }
            else:
                data_set = {
                    'LogisticsType': '',
                    'LogisticsSubType': '',
                }

            data_set.update({
                'ReferenceNo': self.id,
                'GoodsAmount': self.amount_total,
            })
            shipping = self.env['shipping.ecpay.model'].search([('ReferenceNo', '=', self.id)], limit=1)

            shipping.update(data_set) if any(shipping) else shipping.create(data_set)

        return update_complete
