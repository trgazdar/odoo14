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
from odoo.exceptions import UserError, Warning
import logging
_logger = logging.getLogger(__name__)

class SlideChannel(models.Model):
    _inherit = 'slide.channel'

    seller_id = fields.Many2one(
        string="Marketplace Seller",
        comodel_name="res.partner",
        domain=[('seller', '=', True)],
        help="Marketplace seller",
        default=lambda self: self.env.user.partner_id.id if self.env.user.partner_id and self.env.user.partner_id.seller else self.env['res.partner'],
        required = True,
    )

    enroll = fields.Selection(selection_add=[('payment','On payment')],
        default='payment', string='Enroll Policy', required=True,
        help='Condition to enroll: on payment (sale bridge).')
    state = fields.Selection([('new', 'New'), ('pending', 'Pending'), (
        'approved', 'Approved'), ('rejected', 'Rejected')], "Marketplace State", default="new", copy=False, track_visibility='onchange')

    @api.model
    def create(self,vals):
        if vals.get('enroll') and vals.get('enroll') != 'payment':
            raise UserError("The enrollment type is not set as payment")
        return super(SlideChannel,self).create(vals)


    def write(self, vals):
        if vals.get('enroll') and vals.get('enroll') != 'payment':
            raise UserError("The enrollment type is not set as payment")
        return super(SlideChannel,self).write(vals)
    
    def website_publish_button(self):
        for obj in self:
            if obj.product_id.website_published:
                return super(SlideChannel,self).website_publish_button()
            else:
                raise UserError(
                    _("Product of this course is not published."))
        #  super(SlideChannel,self).website_publish_button()

    def approved(self):
        for obj in self:
            if not obj.seller_id:
                raise UserError(_("Marketplace seller id is not assign to this course."))
            if obj.seller_id.state == "approved" and obj.product_id.status == "approved":
                obj.sudo().write({"state": "approved"})
            else:
                raise UserError(
                    _("Marketplace seller or Product of this course is not approved."))
        return True

    def reject(self):
        for course_obj in self:
            if course_obj.state in ("new", "pending", "approved") and course_obj.seller_id:
                course_obj.write({
                    "is_published": False,
                    "state": "rejected"
                })
        return True

    def set_pending(self):
        for course_obj in self:
            if course_obj.state in ("new","rejected") and course_obj.seller_id:
                course_obj.write({
                    "state": "pending"
                })
            else:
                raise Warning(_("Marketplace seller id is not assign to this course."))
        return True

    def mp_action_view_slides(self):
        kanban_view_ref = self.env.ref('marketplace_elearning.mp_slide_slide_view_kanban')
        form_view_ref = self.env.ref('marketplace_elearning.mp_view_slide_slide_form')
        tree_view_ref = self.env.ref('marketplace_elearning.mp_view_slide_slide_tree')
 
        action = {
            'name': 'Course Course',
            'domain': [('channel_id', '=', self.id), ('is_category', '=', False)],
            'res_model': 'slide.slide',
            'type': 'ir.actions.act_window',
            'view_mode': 'kanban,tree,form',
            'views': [(kanban_view_ref.id, 'kanban'), (form_view_ref.id, 'form'), (tree_view_ref.id, 'tree')],
            'context': {'search_default_published': 1,'default_channel_id': self.id},
        }
        return action


class SlideSlide(models.Model):
    _inherit = 'slide.slide'


    seller_id = fields.Many2one(
        string="Marketplace Seller",
        comodel_name="res.partner",
        related='channel_id.seller_id',
        help="Marketplace seller",
    )

    slide_partner_ids = fields.One2many('slide.slide.partner', 'slide_id', string='Subscribers information', groups='website.group_website_publisher, odoo_marketplace.marketplace_seller_group', copy=False)


class RatingRating(models.Model):
    _inherit = 'rating.rating'

    seller_id = fields.Many2one(
        string="Marketplace Seller",
        comodel_name="res.partner",
        domain=[('seller', '=', True)],
        help="Marketplace seller",
        default=lambda self: self.env.user.partner_id.id if self.env.user.partner_id and self.env.user.partner_id.seller else self.env['res.partner']
    )

    def action_open_rated_object(self):
        self.ensure_one()
        form_view_ref = self.env.ref('marketplace_elearning.mp_slide_channel_form')
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'slide.channel',
            'res_id': self.res_id,
            'views': [[form_view_ref.id, 'form']]
        }