
import time
import logging
from odoo import api, fields, models, _
import pprint

_logger = logging.getLogger(__name__)


class account_move(models.Model):
    _name = 'account.move'
    _inherit = ['account.move', 'mail.thread']
    active = fields.Boolean('Active', default=True)
    date = fields.Date(required=True,
                       states={'posted': [('readonly', True)]}, index=True,
                       string="Tanggal",
                       default=fields.Date.context_today)

    # 20191014 列印狀態、列印時間要是"不複製"的欄位
    print_already = fields.Boolean(
        string="列印狀態", default=False, copy=False, track_visibility='onchange')
    print_datetime = fields.Datetime(
        string="列印時間", copy=False, track_visibility='onchange')

    def write(self, values):
        # pprint.pprint(values)
        # 20191014 當日期(date), 參考(ref), 日記帳(journal_id), 日記帳項目(line_ids)有修改時,
        # 把列印狀況改為不勾選
        if values.get('date') or values.get('ref') or values.get('journal_id') or values.get('line_ids'):
            if not self.env.context.get('account_move_writing'):
                self.with_context(account_move_writing=True).write(
                    {'print_already': False})
#        if values.get('date', False):
#            # 當日期更改時, 改變名稱
#            for move in self:
#                sequence = move._get_sequence()
#                if not sequence:
#                    raise UserError(
#                        _('Please define a sequence on your journal.'))
#                values.update({'name': sequence.next_by_id(sequence_date=values.get('date'))})
        return super().write(values)  # python 3


class AccountMoveReport(models.AbstractModel):
    _name = 'report.account_print_journal_voucher.account_move_report'

    @api.model
    def get_report_values(self, docids, data=None):
        return self.common_get_report_values(docids, data)

    @api.model
    def _get_report_values(self, docids, data=None):
        return self.common_get_report_values(docids, data)

    def common_get_report_values(self, docids, data):
        reports = self.env['account.move'].browse(docids)
        for report in reports:
            report.print_already = True
            report.print_datetime = fields.Datetime.now()
        return {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'data': data,
            'docs': reports,
        }
