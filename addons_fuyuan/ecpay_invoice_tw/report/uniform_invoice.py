
from odoo import models, fields, api
from odoo.exceptions import UserError

class ReportEcpayInvoice(models.AbstractModel):
    _name = 'report.ecpay_invoice_tw.invoice'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['account.move'].browse(docids)
        ecpay_invoice = self.env['uniform.invoice']
        for line in docs:
            if line.uniform_state == 'invoiced':
                ecpay_invoice += line.ecpay_invoice_id
            else:
                raise UserError('不能列印有未開或已作廢的電子發票!!')
        return {
            'doc_ids': ecpay_invoice.ids,
            'doc_model': 'uniform.invoice',
            'docs': ecpay_invoice,
        }
