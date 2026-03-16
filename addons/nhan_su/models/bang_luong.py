# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta


class BangLuong(models.Model):
    _name = 'bang.luong'
    _description = 'Bảng lương nhân viên'
    _order = 'thang desc, nam desc'

    name = fields.Char("Mã bảng lương", compute='_compute_name', store=True)
    nhan_vien_id = fields.Many2one('nhan.vien', string="Nhân viên", required=True, ondelete='cascade')
    
    # Thời gian
    thang = fields.Selection([
        ('1', 'Tháng 1'), ('2', 'Tháng 2'), ('3', 'Tháng 3'),
        ('4', 'Tháng 4'), ('5', 'Tháng 5'), ('6', 'Tháng 6'),
        ('7', 'Tháng 7'), ('8', 'Tháng 8'), ('9', 'Tháng 9'),
        ('10', 'Tháng 10'), ('11', 'Tháng 11'), ('12', 'Tháng 12'),
    ], string="Tháng", required=True)
    nam = fields.Integer("Năm", required=True, default=lambda self: fields.Date.today().year)
    
    # Lương cơ bản
    luong_co_ban = fields.Float("Lương cơ bản", required=True)
    
    # Chấm công
    so_ngay_cong_chuan = fields.Integer("Số ngày công chuẩn", default=26)
    so_ngay_cong_thuc_te = fields.Integer("Số ngày công thực tế", compute='_compute_cham_cong', store=True, compute_sudo=True)
    luong_ngay = fields.Float("Lương ngày", compute='_compute_luong_ngay', store=True, compute_sudo=True)
    
    # Các khoản
    phu_cap = fields.Float("Phụ cấp", default=0)
    thuong = fields.Float("Thưởng", default=0)
    tong_phat = fields.Float("Tổng phạt", compute='_compute_cham_cong', store=True, compute_sudo=True)
    tong_OT = fields.Float("Tổng OT", compute='_compute_cham_cong', store=True, compute_sudo=True)
    
    # Tổng lương
    tong_luong = fields.Float("Tổng lương", compute='_compute_tong_luong', store=True, compute_sudo=True)
    
    # Trạng thái
    trang_thai = fields.Selection([
        ('nhap', 'Nháp'),
        ('xac_nhan', 'Xác nhận'),
        ('da_tra', 'Đã trả'),
    ], string="Trạng thái", default='nhap')
    
    ngay_tra_luong = fields.Date("Ngày trả lương")
    ghi_chu = fields.Text("Ghi chú")
    
    # Liên kết chấm công (dùng compute thay vì domain)
    cham_cong_ids = fields.Many2many('cham.cong', string="Chấm công", compute='_compute_cham_cong', store=False, compute_sudo=True)
    
    @api.depends('nhan_vien_id', 'thang', 'nam')
    def _compute_name(self):
        for record in self:
            if record.nhan_vien_id and record.thang and record.nam:
                record.name = f"BL-{record.nhan_vien_id.ma_dinh_danh}-{record.thang}/{record.nam}"
            else:
                record.name = "Mới"
    
    def _get_first_day(self):
        if self.thang and self.nam:
            return datetime(self.nam, int(self.thang), 1).date()
        return fields.Date.today()
    
    def _get_last_day(self):
        if self.thang and self.nam:
            first_day = datetime(self.nam, int(self.thang), 1)
            last_day = first_day + relativedelta(months=1) - relativedelta(days=1)
            return last_day.date()
        return fields.Date.today()
    
    @api.depends('nhan_vien_id', 'thang', 'nam')
    def _compute_cham_cong(self):
        for record in self:
            if record.nhan_vien_id and record.thang and record.nam:
                first_day = record._get_first_day()
                last_day = record._get_last_day()
                
                cham_congs = self.env['cham.cong'].search([
                    ('nhan_vien_id', '=', record.nhan_vien_id.id),
                    ('ngay_cham', '>=', first_day),
                    ('ngay_cham', '<=', last_day),
                    ('trang_thai', '=', 'hoan_thanh')
                ])
                
                record.cham_cong_ids = cham_congs
                record.so_ngay_cong_thuc_te = len(cham_congs)
                record.tong_phat = sum(cham_congs.mapped('tien_phat'))
                record.tong_OT = sum(cham_congs.mapped('tien_OT'))
            else:
                record.cham_cong_ids = False
                record.so_ngay_cong_thuc_te = 0
                record.tong_phat = 0
                record.tong_OT = 0
    
    @api.depends('luong_co_ban', 'so_ngay_cong_chuan')
    def _compute_luong_ngay(self):
        for record in self:
            if record.so_ngay_cong_chuan > 0:
                record.luong_ngay = record.luong_co_ban / record.so_ngay_cong_chuan
            else:
                record.luong_ngay = 0
    
    @api.depends('luong_ngay', 'so_ngay_cong_thuc_te', 'phu_cap', 'thuong', 'tong_phat', 'tong_OT')
    def _compute_tong_luong(self):
        for record in self:
            luong_theo_cong = record.luong_ngay * record.so_ngay_cong_thuc_te
            record.tong_luong = luong_theo_cong + record.phu_cap + record.thuong - record.tong_phat + record.tong_OT
    
    def action_xac_nhan(self):
        self.write({'trang_thai': 'xac_nhan'})
    
    def action_tra_luong(self):
        self.write({
            'trang_thai': 'da_tra',
            'ngay_tra_luong': fields.Date.today()
        })
