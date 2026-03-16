# -*- coding: utf-8 -*-
from odoo import models, fields, api


class BaoCao(models.Model):
    _name = 'bao.cao'
    _description = 'Báo cáo văn bản'

    name = fields.Char("Tên báo cáo", required=True)
    loai_bao_cao = fields.Selection([
        ('van_ban_den', 'Báo cáo văn bản đến'),
        ('van_ban_di', 'Báo cáo văn bản đi'),
        ('tong_hop', 'Báo cáo tổng hợp'),
    ], string="Loại báo cáo", required=True)
    
    tu_ngay = fields.Date("Từ ngày", required=True)
    den_ngay = fields.Date("Đến ngày", required=True)
    
    nguoi_tao = fields.Many2one('res.users', string="Người tạo", default=lambda self: self.env.user)
    ngay_tao = fields.Datetime("Ngày tạo", default=fields.Datetime.now)
    
    mo_ta = fields.Text("Mô tả")
    
    so_van_ban_den = fields.Integer("Số văn bản đến", compute='_compute_thong_ke')
    so_van_ban_di = fields.Integer("Số văn bản đi", compute='_compute_thong_ke')
    
    @api.depends('tu_ngay', 'den_ngay', 'loai_bao_cao')
    def _compute_thong_ke(self):
        for record in self:
            if record.tu_ngay and record.den_ngay:
                # Đếm văn bản đến
                record.so_van_ban_den = self.env['van.ban.den'].search_count([
                    ('ngay_den', '>=', record.tu_ngay),
                    ('ngay_den', '<=', record.den_ngay),
                ])
                # Đếm văn bản đi
                record.so_van_ban_di = self.env['van.ban.di'].search_count([
                    ('ngay_di', '>=', record.tu_ngay),
                    ('ngay_di', '<=', record.den_ngay),
                ])
            else:
                record.so_van_ban_den = 0
                record.so_van_ban_di = 0
