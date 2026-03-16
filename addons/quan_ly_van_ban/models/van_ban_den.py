# -*- coding: utf-8 -*-
from odoo import models, fields, api


class VanBanDen(models.Model):
    _name = 'van.ban.den'
    _description = 'Văn bản đến'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Số văn bản", required=True, tracking=True)
    so_den = fields.Char("Số đến", required=True, tracking=True)
    ngay_den = fields.Date("Ngày đến", default=fields.Date.today, required=True, tracking=True)
    ngay_van_ban = fields.Date("Ngày văn bản", tracking=True)
    
    loai_van_ban_id = fields.Many2one('loai.van.ban', string="Loại văn bản", tracking=True)
    
    co_quan_ban_hanh = fields.Char("Cơ quan ban hành", tracking=True)
    trich_yeu = fields.Text("Trích yếu", required=True, tracking=True)
    
    nguoi_nhan_ids = fields.Many2many('nguoi.nhan', string="Người nhận/Phối hợp")
    
    file_dinh_kem = fields.Binary("File đính kèm")
    file_name = fields.Char("Tên file")
    
    trang_thai = fields.Selection([
        ('moi', 'Mới'),
        ('dang_xu_ly', 'Đang xử lý'),
        ('hoan_thanh', 'Hoàn thành'),
    ], string="Trạng thái", default='moi', tracking=True)
    
    ghi_chu = fields.Text("Ghi chú")
    active = fields.Boolean("Kích hoạt", default=True)
