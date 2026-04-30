from odoo import models, fields, api


class RegistrasiAsesi(models.Model):
    _name = 'registrasi.asesi'
    _description = 'Asesi untuk registrasi'

    name = fields.Char(string='Nama Asesi', required=True)
    identity_number = fields.Char(string='No. Identitas')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Telepon')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ], default='draft', string='Status')
