from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LSPStudent(models.Model):
    _name = 'lsp.student'
    _description = 'Student Registration for LSP'
    _rec_name = 'email'

    # Link to res.users
    user_id = fields.Many2one('res.users', string='User Account', required=True, ondelete='cascade')
    
    # Personal Data
    email = fields.Char(string='Email', required=True)
    full_name = fields.Char(string='Nama Lengkap', required=True)
    nik = fields.Char(string='NIK (No. Induk Kependudukan)', required=True)
    nisn = fields.Char(string='NISN (No. Induk Siswa Nasional)')
    place_of_birth = fields.Char(string='Tempat Lahir')
    date_of_birth = fields.Date(string='Tanggal Lahir')
    gender = fields.Selection([
        ('male', 'Laki-laki'),
        ('female', 'Perempuan'),
    ], string='Jenis Kelamin')
    phone = fields.Char(string='Nomor Telepon')
    address = fields.Text(string='Alamat Lengkap')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ], default='draft', string='Status')
    
    # Education Data
    school = fields.Selection([
        ('smk_negeri_1_rembang', 'SMK Negeri 1 Rembang'),
        ('other', 'Sekolah Lain'),
    ], string='Instansi/Sekolah', required=True)
    
    # Major - if SMK Negeri 1 Rembang
    major_smk = fields.Selection([
        ('teknik_mesin', 'Teknik Mesin'),
        ('teknik_listrik', 'Teknik Listrik'),
        ('teknik_informatika', 'Teknik Informatika'),
        ('akuntansi', 'Akuntansi'),
    ], string='Jurusan (SMK)')
    
    # Major - if other school
    major_other = fields.Char(string='Jurusan Sekolah Lain')
    
    created_at = fields.Datetime(string='Created At', default=fields.Datetime.now)
    
    @api.constrains('email')
    def _check_email_unique(self):
        """Email harus unik"""
        for record in self:
            existing = self.search_count([
                ('email', '=', record.email),
                ('id', '!=', record.id)
            ])
            if existing:
                raise ValidationError(f"Email {record.email} sudah terdaftar.")
    
    @api.constrains('nik')
    def _check_nik_unique(self):
        """NIK harus unik"""
        for record in self:
            existing = self.search_count([
                ('nik', '=', record.nik),
                ('id', '!=', record.id)
            ])
            if existing:
                raise ValidationError(f"NIK {record.nik} sudah terdaftar.")
