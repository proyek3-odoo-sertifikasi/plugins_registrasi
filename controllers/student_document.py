# -*- coding: utf-8 -*-
from odoo import http, fields
from odoo.http import request
import base64
import os
from pathlib import Path


class LSPStudentDocumentController(http.Controller):

    _MAX_UPLOAD_MB = 7
    _MODULE_ROOT = Path(__file__).resolve().parents[1]

    @http.route('/my/registrasi/dokumen', type='http', auth='public', website=True)
    def student_document_page(self, **kwargs):
        # Redirect to login if the user is not authenticated.
        user = request.env.user
        if not user or user._is_public():
            return request.redirect('/web/login?redirect=%s' % request.httprequest.path)

        student = self._get_student_for_current_user()
        if not student:
            return request.render('plugins_registrasi.student_document_template', {
                'errors': ['Data siswa tidak ditemukan. Silakan lakukan pendaftaran terlebih dahulu.'],
                'form_data': {},
                'student': False,
                'document': False,
                'existing_files': {},
                'success_message': False,
                'requirements': self._get_document_requirements(),
            })

        document = request.env['lsp.student.document'].sudo().search([
            ('student_id', '=', student.id)
        ], limit=1)
        success_message = kwargs.get('success') == '1'
        values = self._build_document_template_values(
            student=student,
            document=document,
            success_message=success_message,
        )
        return request.render('plugins_registrasi.student_document_template', values)

    @http.route('/my/registrasi/dokumen/submit', type='http', auth='public', website=True, methods=['POST'])
    def student_document_submit(self, **post):
        user = request.env.user
        if not user or user._is_public():
            return request.redirect('/web/login?redirect=%s' % request.httprequest.path)

        student = self._get_student_for_current_user()
        if not student:
            return request.render('plugins_registrasi.student_document_template', {
                'errors': ['Data siswa tidak ditemukan. Silakan lakukan pendaftaran terlebih dahulu.'],
                'form_data': post,
                'student': False,
                'document': False,
                'existing_files': {},
                'success_message': False,
                'requirements': self._get_document_requirements(),
            })

        document_model = request.env['lsp.student.document'].sudo()
        document = document_model.search([
            ('student_id', '=', student.id)
        ], limit=1)

        updates = {}
        errors = []

        for requirement in self._get_document_requirements():
            upload = request.httprequest.files.get(requirement['field'])
            has_existing = bool(document and getattr(document, requirement['binary_field']))

            if upload and upload.filename:
                valid, result = self._validate_upload(
                    upload=upload,
                    label=requirement['label'],
                    allowed_extensions=requirement['allowed_extensions'],
                )
                if not valid:
                    errors.append(result)
                    continue
                updates[requirement['binary_field']] = result['binary']
                updates[requirement['filename_field']] = result['filename']
            elif not has_existing:
                errors.append('%s wajib diunggah' % requirement['label'])

        if errors:
            values = self._build_document_template_values(
                student=student,
                document=document,
                errors=errors,
                form_data=post,
            )
            return request.render('plugins_registrasi.student_document_template', values)

        if document:
            document.write(updates)
        else:
            updates['student_id'] = student.id
            document = document_model.create(updates)

        if document.is_complete:
            document.write({
                'status': 'submitted',
                'submitted_at': fields.Datetime.now(),
            })

        return request.redirect('/my/registrasi/dokumen?success=1')

    def _get_student_for_current_user(self):
        user = request.env.user
        if not user or user._is_public():
            return False

        return request.env['lsp.student'].sudo().search([
            ('user_id', '=', user.id)
        ], limit=1)

    def _build_document_template_values(self, student, document, errors=None, form_data=None, success_message=False):
        existing_files = {}
        if document:
            for requirement in self._get_document_requirements():
                existing_files[requirement['field']] = getattr(document, requirement['filename_field'])

        return {
            'errors': errors or [],
            'form_data': form_data or {},
            'student': student,
            'document': document,
            'existing_files': existing_files,
            'success_message': success_message,
            'requirements': self._get_document_requirements(),
            'templates': self._get_available_templates(),
        }

    def _validate_upload(self, upload, label, allowed_extensions):
        filename = (upload.filename or '').strip()
        if not filename:
            return False, '%s tidak valid' % label

        extension = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        if extension not in allowed_extensions:
            ext_text = ', '.join(sorted(allowed_extensions))
            return False, '%s harus berformat: %s' % (label, ext_text)

        content = upload.read()
        if not content:
            return False, '%s kosong atau gagal dibaca' % label

        max_bytes = self._MAX_UPLOAD_MB * 1024 * 1024
        if len(content) > max_bytes:
            return False, '%s melebihi batas %sMB' % (label, self._MAX_UPLOAD_MB)

        return True, {
            'binary': base64.b64encode(content).decode('utf-8'),
            'filename': filename,
        }

    def _get_document_requirements(self):
        # Semua upload dibatasi hanya PDF.
        return [
            {
                'field': 'raport_1_5_file',
                'binary_field': 'raport_1_5_file',
                'filename_field': 'raport_1_5_filename',
                'label': 'Salinan Raport 1-5',
                'accept': '.pdf',
                'accept_label': 'PDF',
                'allowed_extensions': {'pdf'},
            },
            {
                'field': 'kartu_pelajar_file',
                'binary_field': 'kartu_pelajar_file',
                'filename_field': 'kartu_pelajar_filename',
                'label': 'Kartu Pelajar',
                'accept': '.pdf',
                'accept_label': 'PDF',
                'allowed_extensions': {'pdf'},
            },
            {
                'field': 'surat_pkl_file',
                'binary_field': 'surat_pkl_file',
                'filename_field': 'surat_pkl_filename',
                'label': 'Salinan Surat Keterangan Telah Melaksanakan PKL',
                'accept': '.pdf',
                'accept_label': 'PDF',
                'allowed_extensions': {'pdf'},
            },
            {
                'field': 'pas_foto_file',
                'binary_field': 'pas_foto_file',
                'filename_field': 'pas_foto_filename',
                'label': 'Pas Foto',
                'accept': '.pdf',
                'accept_label': 'PDF',
                'allowed_extensions': {'pdf'},
            },
            {
                'field': 'asesmen_mandiri_file',
                'binary_field': 'asesmen_mandiri_file',
                'filename_field': 'asesmen_mandiri_filename',
                'label': 'File Asesmen Mandiri',
                'accept': '.pdf',
                'accept_label': 'PDF',
                'allowed_extensions': {'pdf'},
            },
        ]

    @http.route('/my/registrasi/dokumen/template/<string:filename>', type='http', auth='public', website=True)
    def download_template(self, filename, **kwargs):
        # Try static files first, then module root as fallback.
        path = self._MODULE_ROOT / 'static' / 'src' / 'files' / filename
        if not path.exists():
            path = self._MODULE_ROOT / filename

        if not path.exists():
            return request.not_found()

        with open(path, 'rb') as fh:
            data = fh.read()

        headers = [
            ('Content-Type', 'application/pdf'),
            ('Content-Disposition', 'attachment; filename="%s"' % filename),
        ]
        return request.make_response(data, headers)

    def _get_available_templates(self):
        files = []

        static_dir = self._MODULE_ROOT / 'static' / 'src' / 'files'
        if static_dir.is_dir():
            for fname in os.listdir(static_dir):
                if fname.lower().endswith('.pdf'):
                    files.append(fname)

        for fname in os.listdir(self._MODULE_ROOT):
            if fname.lower().endswith('.pdf') and fname not in files:
                files.append(fname)

        return files
