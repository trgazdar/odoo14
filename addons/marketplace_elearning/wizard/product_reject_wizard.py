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

class MpWizardMessage(models.TransientModel):
    _name = "product.reject.wizard"
    _description = "MpWizardMessage"

    text = fields.Html(string='Message')

    def show_confirmation_box(self,course_list = False):
        
        courses = (', ').join([course.name for course in course_list])
        msg = _("These courses are linked with this product if you reject this product, the below courses will also get rejected.")
        msg += "<p style='font-size: 15px'>" + courses + "</p>"
        partial_id = self.create({'text':msg}).id
        form_view_ref = self.env.ref('marketplace_elearning.product_rejection_wizard')
        return {
            'name':'Product Reject' ,
            'binding_view_types': 'form',
            'view_mode': 'form',
            'view_id': form_view_ref.id,
            'res_model': 'product.reject.wizard',
            'res_id': partial_id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }

    def show_unpublish_confirmation_box(self,channel_ids = False):
        
        courses = (', ').join([course.name for course in channel_ids])
        msg = _("These courses are linked with this product if you unpublish this product, the below courses will also get unpublished.")
        msg += "<p style='font-size: 15px'>" + courses + "</p>"
        partial_id = self.create({'text':msg}).id
        form_view_ref = self.env.ref('marketplace_elearning.product_unpublish_wizard')
        return {
            'name':'Product Unpublish',
            'binding_view_types': 'form',
            'view_mode': 'form',
            'view_id': form_view_ref.id,
            'res_model': 'product.reject.wizard',
            'res_id': partial_id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }

    def reject_course_product(self):
        product_obj = self.env['product.template'].search([('id','=',self._context.get('active_id'))],limit=1)
        

        if product_obj:
            channel_ids = product_obj.product_variant_ids.channel_ids
            product_obj.write({
                "sale_ok": False,
                "website_published": False,
                "status": "rejected"
            })
            product_obj.check_state_send_mail()
            if channel_ids:
                for course in channel_ids:
                    course.write({
                        "is_published": False,
                        "state": "rejected"
                    })

    def unpublished_course_product(self):
        product_obj = self.env[self._context.get('active_model')].search([('id','=',self._context.get('active_id'))],limit=1)
        
        if product_obj:
            if self._context.get('active_model') == 'product.template':
                channel_ids = product_obj.product_variant_ids.channel_ids
            else:
                channel_ids = product_obj.channel_ids
            product_obj.write({
                "website_published": False,
            })
            if channel_ids:
                for course in channel_ids:
                    course.write({
                        "is_published": False,
                    })