# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError
import re


class LSPSignupController(http.Controller):
    
    @http.route('/lsp/signup', type='http', auth='public', website=True)
    @http.route('/lsp/signup/', type='http', auth='public', website=True)
    def signup_page(self, **kwargs):
        """Display signup form"""
        values = {
            'form_data': {},
            'errors': [],
            'success_message': False,
            'schools': [
                ('smk_negeri_1_rembang', 'SMK Negeri 1 Rembang'),
                ('other', 'Sekolah Lain'),
            ],
            'majors_smk': [
                ('teknik_mesin', 'Teknik Mesin'),
                ('teknik_listrik', 'Teknik Listrik'),
                ('teknik_informatika', 'Teknik Informatika'),
                ('akuntansi', 'Akuntansi'),
            ],
            'genders': [
                ('male', 'Laki-laki'),
                ('female', 'Perempuan'),
            ],
        }
        return request.render('plugins_registrasi.signup_template', values)
    
    @http.route('/lsp/signup/submit', type='http', auth='public', website=True, methods=['POST'])
    def signup_submit(self, **post):
        """Handle signup form submission"""
        try:
            # Extract form data
            email = post.get('email', '').strip()
            password = post.get('password', '').strip()
            confirm_password = post.get('confirm_password', '').strip()
            full_name = post.get('full_name', '').strip()
            nik = post.get('nik', '').strip()
            nisn = post.get('nisn', '').strip()
            place_of_birth = post.get('place_of_birth', '').strip()
            date_of_birth = post.get('date_of_birth', '')
            gender = post.get('gender', '')
            phone = post.get('phone', '').strip()
            address = post.get('address', '').strip()
            school = post.get('school', '')
            major_smk = post.get('major_smk', '')
            major_other = post.get('major_other', '').strip()
            
            # Validation
            errors = []
            
            # Email validation
            if not email:
                errors.append('Email tidak boleh kosong')
            elif not self._is_valid_email(email):
                errors.append('Format email tidak valid')
            
            # Check email uniqueness
            existing_user = request.env['res.users'].sudo().search_count([
                ('login', '=', email)
            ])
            if existing_user:
                errors.append('Email sudah terdaftar')
            
            existing_student = request.env['lsp.student'].sudo().search_count([
                ('email', '=', email)
            ])
            if existing_student:
                errors.append('Email sudah terdaftar sebagai siswa')
            
            # Password validation
            if not password:
                errors.append('Password tidak boleh kosong')
            elif len(password) < 6:
                errors.append('Password minimal 6 karakter')
            elif password != confirm_password:
                errors.append('Password dan konfirmasi password tidak cocok')
            
            # Full name validation
            if not full_name:
                errors.append('Nama lengkap tidak boleh kosong')
            
            # NIK validation
            if not nik:
                errors.append('NIK tidak boleh kosong')
            elif not nik.isdigit() or len(nik) != 16:
                errors.append('NIK harus 16 digit angka')
            
            # Gender validation
            if not gender or gender not in ['male', 'female']:
                errors.append('Jenis kelamin harus dipilih')
            
            # School validation
            if not school or school not in ['smk_negeri_1_rembang', 'other']:
                errors.append('Sekolah harus dipilih')
            
            # Major validation
            if school == 'smk_negeri_1_rembang' and not major_smk:
                errors.append('Jurusan SMK harus dipilih')
            elif school == 'other' and not major_other:
                errors.append('Jurusan sekolah harus diisi')
            
            if errors:
                return request.render('plugins_registrasi.signup_template', {
                    'errors': errors,
                    'form_data': post,
                    'schools': [
                        ('smk_negeri_1_rembang', 'SMK Negeri 1 Rembang'),
                        ('other', 'Sekolah Lain'),
                    ],
                    'majors_smk': [
                        ('teknik_mesin', 'Teknik Mesin'),
                        ('teknik_listrik', 'Teknik Listrik'),
                        ('teknik_informatika', 'Teknik Informatika'),
                        ('akuntansi', 'Akuntansi'),
                    ],
                    'genders': [
                        ('male', 'Laki-laki'),
                        ('female', 'Perempuan'),
                    ],
                })
            
            # Create partner and user with sudo
            env = request.env
            
            # Create res.partner
            partner = env['res.partner'].sudo().create({
                'name': full_name,
                'email': email,
                'phone': phone,
                'type': 'contact',
            })
            
            # Get portal group
            portal_group = env.ref('base.group_portal')
            
            # Create res.users
            new_user = env['res.users'].sudo().create({
                'name': full_name,
                'login': email,
                'email': email,
                'password': password,
                'partner_id': partner.id,
                'groups_id': [(6, 0, [portal_group.id])],
                'active': True,
            })
            
            # Create lsp.student
            student_data = {
                'user_id': new_user.id,
                'email': email,
                'full_name': full_name,
                'nik': nik,
                'nisn': nisn or False,
                'place_of_birth': place_of_birth or False,
                'date_of_birth': date_of_birth or False,
                'gender': gender,
                'phone': phone or False,
                'address': address or False,
                'school': school,
            }
            
            if school == 'smk_negeri_1_rembang':
                student_data['major_smk'] = major_smk
            else:
                student_data['major_other'] = major_other
            
            student = env['lsp.student'].sudo().create(student_data)
            
            # Success - redirect to login with message
            request.session['signup_success'] = True
            request.session['signup_email'] = email
            return request.redirect('/web/login')
            
        except ValidationError as e:
            errors = [e.name or str(e)]
            return request.render('plugins_registrasi.signup_template', {
                'errors': errors,
                'form_data': post,
                'schools': [
                    ('smk_negeri_1_rembang', 'SMK Negeri 1 Rembang'),
                    ('other', 'Sekolah Lain'),
                ],
                'majors_smk': [
                    ('teknik_mesin', 'Teknik Mesin'),
                    ('teknik_listrik', 'Teknik Listrik'),
                    ('teknik_informatika', 'Teknik Informatika'),
                    ('akuntansi', 'Akuntansi'),
                ],
                'genders': [
                    ('male', 'Laki-laki'),
                    ('female', 'Perempuan'),
                ],
            })
        except Exception as e:
            errors = [f'Terjadi kesalahan: {str(e)}']
            return request.render('plugins_registrasi.signup_template', {
                'errors': errors,
                'form_data': post,
                'schools': [
                    ('smk_negeri_1_rembang', 'SMK Negeri 1 Rembang'),
                    ('other', 'Sekolah Lain'),
                ],
                'majors_smk': [
                    ('teknik_mesin', 'Teknik Mesin'),
                    ('teknik_listrik', 'Teknik Listrik'),
                    ('teknik_informatika', 'Teknik Informatika'),
                    ('akuntansi', 'Akuntansi'),
                ],
                'genders': [
                    ('male', 'Laki-laki'),
                    ('female', 'Perempuan'),
                ],
            })
    
    def _is_valid_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
