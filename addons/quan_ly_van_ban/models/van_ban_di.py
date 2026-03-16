# -*- coding: utf-8 -*-
from odoo import models, fields, api


class VanBanDi(models.Model):
    _name = 'van.ban.di'
    _description = 'Văn bản đi'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Số văn bản", required=True, tracking=True)
    so_di = fields.Char("Số đi", required=True, tracking=True)
    ngay_di = fields.Date("Ngày đi", default=fields.Date.today, required=True, tracking=True)
    
    loai_van_ban_id = fields.Many2one('loai.van.ban', string="Loại văn bản", tracking=True)
    
    don_vi_nhan = fields.Char("Đơn vị nhận", tracking=True)
    trich_yeu = fields.Text("Trích yếu", required=True, tracking=True)
    
    nguoi_ky = fields.Many2one('res.users', string="User ký", tracking=True)
    nguoi_nhan_ids = fields.Many2many('nguoi.nhan', string="Người nhận/Phối hợp")
    
    file_dinh_kem = fields.Binary("File đính kèm")
    file_name = fields.Char("Tên file")
    
    trang_thai = fields.Selection([
        ('nhap', 'Nháp'),
        ('cho_ky', 'Chờ ký'),
        ('da_ky', 'Đã ký'),
        ('da_gui', 'Đã gửi'),
    ], string="Trạng thái", default='nhap', tracking=True)
    
    ghi_chu = fields.Text("Ghi chú")
    active = fields.Boolean("Kích hoạt", default=True)
