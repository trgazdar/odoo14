# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def create(self, vals):
        if vals.get('type', False) and vals['type'] == 'service':
            vals["invoice_policy"] = "order"
        product_template = super(ProductTemplate, self).create(vals)
        return product_template

    def toggle_website_published(self):
        for record in self:
            if record.website_published and record.product_variant_ids.channel_ids:
                channel_ids = record.product_variant_ids.channel_ids
                res = self.env['product.reject.wizard'].show_unpublish_confirmation_box(channel_ids)
                return res
        return super().toggle_website_published()

    def reject(self):
        for product_obj in self:
            if product_obj.product_variant_ids and product_obj.product_variant_ids.channel_ids:
                channel_ids = product_obj.product_variant_ids.channel_ids
                res = self.env['product.reject.wizard'].show_confirmation_box(channel_ids)
                return res
        return super(ProductTemplate, self).reject()

class ProductProduct(models.Model):
    _inherit = "product.product"

    def website_publish_button(self):
        for record in self:
            if record.website_published and record.channel_ids:
                channel_ids = record.channel_ids
                res = self.env['product.reject.wizard'].show_unpublish_confirmation_box(channel_ids)
                return res
        return super().website_publish_button()
