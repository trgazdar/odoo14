# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import pprint
import logging
from werkzeug import urls
from odoo import http, _
from odoo.http import request
from odoo.addons.logistic_ecpay.controllers.ecpay_logistic_sdk import ECPayLogisticSdk

_logger = logging.getLogger(__name__)


class WebsiteSaleDeliveryEcpay(http.Controller):

    CVSStoreID = ""
    CVSStoreName = ""
    CVSAddress = ""
    CVSTelephone = ""
    ecpay_logistic_sdk = 0

    _ServerReplyURL = '/logistic/ecpay/server_reply_url'

    @http.route('/logistic/ecpay/server_reply_url', type='http', methods=['POST'], auth="public", website=True, csrf=False)
    def server_reply_url(self, **post):
        """
        物流狀態通知
        每當物流狀態有變更時，綠界科技皆會傳送物流狀態至合作特店。
        1.綠界科技：以 ServerPost 方式傳送物流狀態至合作特店設定的(ServerReplyURL) 網址
        2.合作特店：收到綠界科技的物流狀態，並判斷檢查碼是否相符
        3.合作特店：檢查碼相符後，在網頁端回應 1|OK
        """
        _logger.info('綠界回傳[物流狀態通知] %s',
                     pprint.pformat(post))
        #  計算驗證 CheckMacValue 是否相符
        if request.env['shipping.ecpay.model'].sudo().ecpay_check_mac_value(post):
            # 先建立一筆物流資料在資料庫
            request.env['shipping.ecpay.model'].sudo(
            ).shipping_ecpay_model_update(post)
            return '1|OK'
        else:
            return '0|error'

    @http.route(['/logistics/reply'], type='http', auth='public', csrf=False, website=True)
    def logistics_reply(self, **post):
        """
        綠界會將店鋪資訊回傳到此 router
        """
        #pprint.pprint(post)
        if post.get('webPara') == 'ezShip':
            self.CVSStoreID = post.get('stCode')
            self.CVSStoreName = post.get('stName')
            self.CVSAddress = post.get('stAddr')
        else:
            self.CVSStoreID = post.get('CVSStoreID')
            self.CVSStoreName = post.get('CVSStoreName')
            self.CVSAddress = post.get('CVSAddress')
        response = request.render("logistic_ecpay.map_logistic_ecpay")
        return response

    @http.route(['/shipping/update_carrier'], type='json', auth='public', methods=['POST'], website=True, csrf=False)
    def update_eshop_carrier(self, **post):
        """
        利用 ajax 將店鋪資訊回傳給前端
        """
        data = {
            'CVSStoreID': self.CVSStoreID,
            'CVSStoreName': self.CVSStoreName,
            'CVSAddress': self.CVSAddress,
        }
        self.CVSStoreID = ''
        self.CVSStoreName = ''
        self.CVSAddress = ''
        return data

    @http.route(['/shipping/map', '/shipping/map/<LogisticsSubType>'], type='http', auth="public", website=True, csrf=False)
    def cvs_map(self, LogisticsSubType, **post):
        # 取得 ECPay 的後台設定值
        ecpay_setting = request.env['delivery.carrier'].sudo().search(
            [('delivery_type', '=', 'ecpay')], limit=1)
        # 取得 domain
        base_url = ecpay_setting.ecpay_domain if ecpay_setting.ecpay_domain else request.env['ir.config_parameter'].sudo(
        ).get_param('web.base.url')
        # 建立實體
        values = dict()
        if LogisticsSubType == 'UNIMART':
            self.ecpay_logistic_sdk = ECPayLogisticSdk(
                MerchantID=ecpay_setting.MerchantID,
                HashKey=ecpay_setting.HashKey,
                HashIV=ecpay_setting.HashIV)

            if ecpay_setting.ecpay_type == 'c2c':
                LogisticsSubType = LogisticsSubType + 'C2C'

            parameter = {
                "MerchantTradeNo": "anyno",
                "LogisticsType": "CVS",
                "LogisticsSubType": LogisticsSubType,
                "IsCollection": "N",
                "ServerReplyURL": urls.url_join(base_url, "/logistics/reply"),
                "ExtraData": "",
                "Device": 0,
            }
            values['ecpay_url'] = request.env['shipping.ecpay.model'].sudo(
            ).get_ecpay_urls(ecpay_setting.prod_environment)['CVS_MAP']
            parameter = self.ecpay_logistic_sdk.cvs_map(parameter)
        elif LogisticsSubType == 'EZSHIP':
            parameter = {
                'suID': 'zen0523@gmail.com',
                'processID': '123',
                'stCate': '',
                'stCode': '',
                'rtURL': urls.url_join(base_url, "/logistics/reply"),
                'webPara': 'ezShip',
            }
            values['ecpay_url'] = 'https://map.ezship.com.tw/ezship_map_web.jsp'
        # pprint.pprint(parameter)
        values['parameters'] = parameter
        return request.render("logistic_ecpay.ecpay_logistic_form", values)

    @http.route('/shipping/save_shipping_info', type='json', methods=['POST'], auth="public")
    def save_shipping_info(self, **post):
        """
        利用 ajax 將店鋪資訊回傳給前端
        """
        shipping_info = post['shipping_info_package']
        session_info = request.session
        sale_order = request.env['sale.order'].sudo().browse(session_info.get('sale_order_id', 0))

        if not any(sale_order):
            return {}

        params = {
            'ReferenceNo': sale_order.id,
            'ReceiverName': shipping_info.get('receiver_name'),
            'ReceiverCellPhone': shipping_info.get('receiver_mobile'),
            'ReceiverZipCode': shipping_info.get('home_zip_code'),
            'ReceiverAddress': shipping_info.get('home_address'),
            'CVSStoreID': shipping_info.get('cvs_id'),
            'CVSStoreName': shipping_info.get('shipping_store'),
        }
        # 先建立一筆物流資料在資料庫
        request.env['shipping.ecpay.model'].sudo().shipping_ecpay_model_record(params)

    @http.route('/shipping/get_delivery_method_name', type='json', methods=['POST'], auth="public")
    def get_delivery_method_name(self, **post):
        try:
            post_id = int(post['id'])
        except:
            post_id = 0

        return request.env['delivery.carrier'].sudo().get_delivery_method_name(post_id)
