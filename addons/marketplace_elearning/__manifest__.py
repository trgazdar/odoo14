# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
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
{
  "name"                 :  "Odoo eLearning Marketplace",
  "summary"              :  """Odoo Marketplace eLearning, this module allows marketplace sellers to sell Online Courses""",
  "category"             :  "Website",
  "version"              :  "1.0.1",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/",
  "description"          :  """Odoo Marketplace eLearning,
  Marketplace eLearning,
  eLearning""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=marketplace_elearning&lifetime=120&lout=0",
  "depends"              :  [
                             'website_sale_slides',
                             'odoo_marketplace',
                            ],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'security/mp_elearning_security.xml',
                             'wizard/project_reject_wizard.xml',
                             'views/elearning_slide_channel_inherit.xml',
                             'views/elarning_slide_content_inherit.xml',
                             'views/mp_slide_channel_tag_inherit.xml',
                             'views/mp_rating_rating_view.xml',
                             'views/mp_slide_channel_tag_view.xml',
                             'views/mp_slide_content_tag_view.xml',
                             'views/mp_elearning_menu.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  99,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}
