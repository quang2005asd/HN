# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta


class ChamCong(models.Model):
    _name = 'cham.cong'
    _description = 'Chấm công nhân viên'
    _order = 'ngay_cham desc'

    name = fields.Char("Mã chấm công", compute='_compute_name', store=True)
    nhan_vien_id = fields.Many2one('nhan.vien', string="Nhân viên", required=True, ondelete='cascade')
    ngay_cham = fields.Date("Ngày chấm", required=True, default=fields.Date.today)
    gio_vao = fields.Datetime("Giờ vào", required=True)
    gio_ra = fields.Datetime("Giờ ra")
    
    # Tính toán tự động
    so_gio_lam = fields.Float("Số giờ làm", compute='_compute_gio_lam', store=True)
    gio_lam_thieu = fields.Float("Giờ làm thiếu", compute='_compute_gio_lam', store=True)
    gio_OT = fields.Float("Giờ OT", default=0)
    
    # Đi muộn về sớm
    di_muon = fields.Boolean("Đi muộn", compute='_compute_vi_pham', store=True)
    ve_som = fields.Boolean("Về sớm", compute='_compute_vi_pham', store=True)
    
    # Phạt và thưởng
    tien_phat = fields.Float("Tiền phạt", compute='_compute_tien_phat', store=True)
    tien_OT = fields.Float("Tiền OT", compute='_compute_tien_OT', store=True)
    
    ghi_chu = fields.Text("Ghi chú")
    trang_thai = fields.Selection([
        ('chua_ra', 'Chưa ra'),
        ('hoan_thanh', 'Hoàn thành'),
        ('thieu_gio', 'Thiếu giờ'),
    ], string="Trạng thái", compute='_compute_trang_thai', store=True)
    
    @api.depends('nhan_vien_id', 'ngay_cham')
    def _compute_name(self):
        for record in self:
            if record.nhan_vien_id and record.ngay_cham:
                record.name = f"CC-{record.nhan_vien_id.ma_dinh_danh}-{record.ngay_cham}"
            else:
                record.name = "Mới"
    
    @api.depends('gio_vao', 'gio_ra')
    def _compute_gio_lam(self):
        for record in self:
            if record.gio_vao and record.gio_ra:
                delta = record.gio_ra - record.gio_vao
                hours = delta.total_seconds() / 3600
                record.so_gio_lam = hours
                record.gio_lam_thieu = max(0, 8 - hours)
            else:
                record.so_gio_lam = 0
                record.gio_lam_thieu = 0
    
    @api.depends('gio_vao', 'gio_ra', 'ngay_cham')
    def _compute_vi_pham(self):
        for record in self:
            if record.gio_vao and record.ngay_cham:
                # Quy định: 8:00 AM là giờ vào chuẩn
                gio_vao_chuan = datetime.combine(record.ngay_cham, datetime.min.time().replace(hour=8, minute=0))
                record.di_muon = record.gio_vao > fields.Datetime.to_datetime(gio_vao_chuan)
            else:
                record.di_muon = False
            
            if record.gio_ra and record.ngay_cham:
                # Quy định: 17:00 PM là giờ ra chuẩn (sau 8 tiếng làm từ 8AM)
                gio_ra_chuan = datetime.combine(record.ngay_cham, datetime.min.time().replace(hour=17, minute=0))
                record.ve_som = record.gio_ra < fields.Datetime.to_datetime(gio_ra_chuan)
            else:
                record.ve_som = False
    
    @api.depends('di_muon', 've_som', 'gio_lam_thieu')
    def _compute_tien_phat(self):
        for record in self:
            tien_phat = 0
            # Phạt đi muộn: 50k
            if record.di_muon:
                tien_phat += 50000
            # Phạt về sớm: 50k
            if record.ve_som:
                tien_phat += 50000
            # Phạt thiếu giờ: 100k/giờ
            if record.gio_lam_thieu > 0:
                tien_phat += record.gio_lam_thieu * 100000
            record.tien_phat = tien_phat
    
    @api.depends('gio_OT')
    def _compute_tien_OT(self):
        for record in self:
            # OT: 50k/giờ
            record.tien_OT = record.gio_OT * 50000
    
    @api.depends('gio_ra', 'so_gio_lam')
    def _compute_trang_thai(self):
        for record in self:
            if not record.gio_ra:
                record.trang_thai = 'chua_ra'
            elif record.so_gio_lam < 8:
                record.trang_thai = 'thieu_gio'
            else:
                record.trang_thai = 'hoan_thanh'
