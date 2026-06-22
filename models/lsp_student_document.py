from odoo import models, fields, api


class LSPStudentDocument(models.Model):
    _name = 'lsp.student.document'
    _description = 'Dokumen Persyaratan Siswa LSP'
    _rec_name = 'student_id'

    student_id = fields.Many2one(
        'lsp.student',
        string='Siswa',
        required=True,
        ondelete='cascade',
        index=True,
    )
    user_id = fields.Many2one(
        'res.users',
        string='Pengguna',
        related='student_id.user_id',
        store=True,
        index=True,
        readonly=True,
    )

    raport_1_5_file = fields.Binary(string='Salinan Raport 1-5', attachment=True)
    raport_1_5_filename = fields.Char(string='Nama File Raport 1-5')

    kartu_pelajar_file = fields.Binary(string='Kartu Pelajar', attachment=True)
    kartu_pelajar_filename = fields.Char(string='Nama File Kartu Pelajar')

    surat_pkl_file = fields.Binary(string='Surat Keterangan PKL', attachment=True)
    surat_pkl_filename = fields.Char(string='Nama File Surat PKL')

    pas_foto_file = fields.Binary(string='Pas Foto', attachment=True)
    pas_foto_filename = fields.Char(string='Nama File Pas Foto')

    asesmen_mandiri_file = fields.Binary(string='File Asesmen Mandiri', attachment=True)
    asesmen_mandiri_filename = fields.Char(string='Nama File Asesmen Mandiri')

    status = fields.Selection(
        [
            ('draft', 'Draft'),
            ('submitted', 'Submitted'),
            ('verified', 'Verified'),
            ('rejected', 'Rejected'),
        ],
        string='Status',
        default='draft',
        required=True,
    )
    school = fields.Selection(
        related='student_id.school',
        string='Instansi/Sekolah',
        readonly=True,
    )
    major_smk = fields.Selection(
        related='student_id.major_smk',
        string='Jurusan (SMK)',
        readonly=False,
    )
    major_other = fields.Char(
        related='student_id.major_other',
        string='Jurusan Sekolah Lain',
        readonly=True,
    )

    def action_verify(self):
        for record in self:
            if record.school == 'other':
                # Open wizard to select major
                return {
                    'name': 'Pilih Skema Sertifikasi',
                    'type': 'ir.actions.act_window',
                    'res_model': 'lsp.student.verify.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_document_id': record.id,
                        'default_school': record.school,
                    }
                }
            
            # If internal, just verify
            record.write({'status': 'verified'})
            if record.student_id:
                record.student_id.write({'state': 'verified'})

    def action_reject(self):
        for record in self:
            record.write({'status': 'rejected'})
            if record.student_id:
                record.student_id.write({'state': 'rejected'})
    submitted_at = fields.Datetime(string='Tanggal Submit')

    is_complete = fields.Boolean(
        string='Dokumen Lengkap',
        compute='_compute_is_complete',
        store=True,
    )

    _sql_constraints = [
        ('student_unique_document', 'unique(student_id)', 'Setiap siswa hanya boleh memiliki satu data dokumen.'),
    ]

    @api.depends(
        'raport_1_5_file',
        'kartu_pelajar_file',
        'surat_pkl_file',
        'pas_foto_file',
        'asesmen_mandiri_file',
    )
    def _compute_is_complete(self):
        for record in self:
            record.is_complete = all([
                record.raport_1_5_file,
                record.kartu_pelajar_file,
                record.surat_pkl_file,
                record.pas_foto_file,
                record.asesmen_mandiri_file,
            ])
