from odoo import models, fields, api
from odoo.exceptions import UserError


class AccountMoveReversalInherit(models.TransientModel):
    _inherit = 'account.move.reversal'

    def reverse_moves(self):
        res = super(AccountMoveReversalInherit, self).reverse_moves()
        context = dict(self._context or {})
        # 取得欲作廢或折讓的應收憑單
        invoices = self.env['account.move'].browse(context.get('active_ids'))
        #TODO 使用search 會導致全部的reversed_entry_id = invoice.id 都會被影響，應該從res 來檢查被創建的reversed moves
        res_id = res.get('res_id', False)
        if res_id:
            reversed_ids = [res_id]
        else:
            reversed_ids = res.get('domain')[0][2]
        out_refunds = self.env['account.move'].browse(reversed_ids)
        for invoice in invoices:
            # 如果沒有產生電子發票則不需做關於電子發票相關動作
            if not invoice.ecpay_invoice_id:
                continue

            reversed_moves = out_refunds.filtered(lambda r: r.reversed_entry_id.id == invoice.id)
            if not reversed_moves:
                continue

            if self.refund_method == 'refund':
                # 設定該折讓單要關聯欲作廢或折讓的統一發票
                reversed_moves.write({
                    'IA_Invoice_No': invoice.ecpay_invoice_id.id,
                    'is_refund': True
                })
            else:
                # 設定該折讓單要關聯欲作廢或折讓的統一發票
                reversed_moves.write({'III_Invoice_No': invoice.ecpay_invoice_id.id})               
                # 執行作廢
                for move in reversed_moves:
                    move.run_invoice_invalid()
                # 將原先欲作廢的發票更新發票狀態
                invoice.uniform_state = 'invalid'

        return res
