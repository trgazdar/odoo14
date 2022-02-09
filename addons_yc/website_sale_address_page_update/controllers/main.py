# -*- coding: utf-8 -*-
from odoo.addons.website_sale.controllers.main import WebsiteSale
# from odoo.http import request


class WebsiteSaleUpdate(WebsiteSale):
    def _get_mandatory_billing_fields(self):
        return ["name", "email", "street"]

    def _get_mandatory_shipping_fields(self):
        return ["name", "street"]

    def _get_mandatory_fields_billing(self, country_id=False):
        req = self._get_mandatory_billing_fields()
        # if country_id:
        #     country = request.env['res.country'].browse(country_id)
        #     if country.state_required:
        #         req += ['state_id']
        #     if country.zip_required:
        #         req += ['zip']
        return req

    def _get_mandatory_fields_shipping(self, country_id=False):
        req = self._get_mandatory_shipping_fields()
        # if country_id:
        #     country = request.env['res.country'].browse(country_id)
        #     if country.state_required:
        #         req += ['state_id']
        #     if country.zip_required:
        #         req += ['zip']
        return req
