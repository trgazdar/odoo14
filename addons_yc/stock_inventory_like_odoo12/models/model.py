# coding: utf-8
import logging
import time
import math
from odoo import api, fields, models, _
from datetime import date, datetime, timedelta
import pprint

_logger = logging.getLogger(__name__)


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    def action_inventory_line_tree(self):
        pass
