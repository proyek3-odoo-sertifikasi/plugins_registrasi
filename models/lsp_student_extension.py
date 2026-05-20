from odoo import models, fields


class LSPStudent(models.Model):
    _inherit = 'lsp.student'

    document_ids = fields.One2many(
        'lsp.student.document',
        'student_id',
        string='Dokumen Persyaratan',
    )
    document_count = fields.Integer(
        string='Jumlah Dokumen',
        compute='_compute_document_count',
    )

    def _compute_document_count(self):
        for record in self:
            record.document_count = len(record.document_ids)
