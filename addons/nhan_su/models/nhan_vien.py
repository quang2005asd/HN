from odoo import models, fields, api


class NhanVien(models.Model):
    _name = 'nhan.vien'
    _description = 'Bảng chứa thông tin nhân viên'

    name = fields.Char("Họ và tên", required=True)
    ma_dinh_danh = fields.Char("Mã định danh", required=True)
    user_id = fields.Many2one('res.users', string="User liên kết", help="Liên kết nhân viên với tài khoản Odoo")
    ngay_sinh = fields.Date("Ngày sinh")
    que_quan = fields.Char("Quê quán")
    vung_mien = fields.Selection([
        ('bac', 'Miền Bắc'),
        ('trung', 'Miền Trung'),
        ('nam', 'Miền Nam'),
    ], string="Vùng miền")
    email = fields.Char("Email")
    so_dien_thoai = fields.Char("Số điện thoại")
    
    # Thông tin công việc
    luong_co_ban = fields.Float("Lương cơ bản", default=0)
    phu_cap = fields.Float("Phụ cấp", default=0)
    
    # Liên kết với chấm công
    cham_cong_ids = fields.One2many('cham.cong', 'nhan_vien_id', string="Chấm công")
    cham_cong_count = fields.Integer("Số lần chấm công", compute='_compute_cham_cong_count')
    
    # Liên kết với bảng lương
    bang_luong_ids = fields.One2many('bang.luong', 'nhan_vien_id', string="Bảng lương")
    bang_luong_count = fields.Integer("Số bảng lương", compute='_compute_bang_luong_count')
    
    @api.depends('cham_cong_ids')
    def _compute_cham_cong_count(self):
        for record in self:
            record.cham_cong_count = len(record.cham_cong_ids)
    
    @api.depends('bang_luong_ids')
    def _compute_bang_luong_count(self):
        for record in self:
            record.bang_luong_count = len(record.bang_luong_ids)

    def action_view_cham_cong(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Chấm công',
            'res_model': 'cham.cong',
            'view_mode': 'tree,form',
            'domain': [('nhan_vien_id', '=', self.id)],
            'context': {'default_nhan_vien_id': self.id}
        }
    
    def action_view_bang_luong(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Bảng lương',
            'res_model': 'bang.luong',
            'view_mode': 'tree,form',
            'domain': [('nhan_vien_id', '=', self.id)],
            'context': {'default_nhan_vien_id': self.id}
        }
