# -*- coding: utf-8 -*-
from odoo import models, fields, api


class PhieuChuyen(models.Model):
    _name = 'phieu.chuyen'
    _description = 'Phiếu chuyển văn bản'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Số phiếu", required=True, readonly=True, default='New')
    ngay_chuyen = fields.Date("Ngày chuyển", default=fields.Date.today, required=True, tracking=True)
    
    van_ban_den_id = fields.Many2one('van.ban.den', string="Văn bản đến")
    van_ban_di_id = fields.Many2one('van.ban.di', string="Văn bản đi")
    
    nguoi_chuyen = fields.Many2one('res.users', string="Người chuyển", default=lambda self: self.env.user, tracking=True)
    nguoi_nhan_id = fields.Many2one('nguoi.nhan', string="Người nhận", required=True, tracking=True)
    
    noi_dung = fields.Text("Nội dung chuyển", required=True)
    ghi_chu = fields.Text("Ghi chú")
    
    trang_thai = fields.Selection([
        ('chua_nhan', 'Chưa nhận'),
        ('da_nhan', 'Đã nhận'),
    ], string="Trạng thái", default='chua_nhan', tracking=True)
    
    ngay_nhan = fields.Datetime("Ngày nhận")
    active = fields.Boolean("Kích hoạt", default=True)
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('phieu.chuyen') or 'New'
        return super(PhieuChuyen, self).create(vals)
