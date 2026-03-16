# -*- coding: utf-8 -*-
from odoo import models, fields, api


class LogHoatDong(models.Model):
    _name = 'log.hoat.dong'
    _description = 'Log hoạt động'
    _order = 'ngay_thuc_hien desc'

    name = fields.Char("Tên hoạt động", required=True)
    ngay_thuc_hien = fields.Datetime("Ngày thực hiện", default=fields.Datetime.now, required=True)
    nguoi_thuc_hien = fields.Many2one('res.users', string="Người thực hiện", default=lambda self: self.env.user)
    
    loai_hoat_dong = fields.Selection([
        ('tao_moi', 'Tạo mới'),
        ('cap_nhat', 'Cập nhật'),
        ('xoa', 'Xóa'),
        ('chuyen', 'Chuyển'),
    ], string="Loại hoạt động", required=True)
    
    mo_ta = fields.Text("Mô tả")
    
    van_ban_den_id = fields.Many2one('van.ban.den', string="Văn bản đến")
    van_ban_di_id = fields.Many2one('van.ban.di', string="Văn bản đi")
