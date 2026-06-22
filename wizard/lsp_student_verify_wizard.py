from odoo import models, fields, api
from odoo.exceptions import UserError


class LSPStudentVerifyWizard(models.TransientModel):
    _name = 'lsp.student.verify.wizard'
    _description = 'Wizard Verifikasi Dokumen Asesi'

    document_id = fields.Many2one('lsp.student.document', string='Dokumen', required=True)
    school = fields.Selection(related='document_id.school')
    major_smk = fields.Selection([
        ('bdp', 'Bisnis Daring dan Pemasaran (BDP)'),
        ('rpl', 'Rekayasa Perangkat Lunak (RPL)'),
        ('tbsm', 'Teknik dan Bisnis Sepeda Motor (TBSM)'),
    ], string='Pilih Jurusan (Skema Sertifikasi)', required=True)

    def action_confirm_verify(self):
        self.ensure_one()
        if not self.major_smk:
            raise UserError("Jurusan harus dipilih untuk memetakan asesi ke skema sertifikasi yang tepat.")
        
        # Update the student's major
        if self.document_id.student_id:
            self.document_id.student_id.write({'major_smk': self.major_smk})
            
        # Verify the document and student
        self.document_id.write({'status': 'verified'})
        if self.document_id.student_id:
            self.document_id.student_id.write({'state': 'verified'})
        
        return {'type': 'ir.actions.act_window_close'}
