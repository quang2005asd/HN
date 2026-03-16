from odoo import models, fields, api
from datetime import timedelta

from odoo.exceptions import ValidationError


class HoTroKhachHang(models.Model):
    _name = 'ho_tro_khach_hang'
    _description = 'Hỗ trợ khách hàng'
    _rec_name = 'ma_ho_tro'

    ma_ho_tro = fields.Char("Mã hỗ trợ", required=True, copy=False, readonly=True,
                            default=lambda self: self.env['ir.sequence'].next_by_code('ho_tro_khach_hang') or 'HT/MỚI')

    # Thông tin khách hàng
    ten_khach_hang = fields.Many2one(
        'thong_tin_khach_hang', string="Khách hàng", required=True
    )

    muc_do_uu_tien = fields.Selection([
        ('thap', 'Thấp'),
        ('trung_binh', 'Trung bình'),
        ('cao', 'Cao'),
        ('khan_cap', 'Khẩn cấp'),
    ], string="Mức độ ưu tiên", default='trung_binh', required=True)

    phuong_thuc_lien_lac = fields.Selection([
        ('call', 'Gọi điện'),
        ('email', 'Email'),
        ('chat', 'Nhắn tin'),
        ('direct', 'Gặp trực tiếp')
    ], string="Phương thức liên lạc", required=True)

    # Thời gian hỗ trợ
    thoi_gian_bat_dau = fields.Datetime(string="Thời gian bắt đầu", required=True)
    thoi_gian_ket_thuc = fields.Datetime(string="Thời gian kết thúc")

    ngay_ho_tro = fields.Integer(
        string="Số ngày hỗ trợ",
        compute="_compute_ngay_ho_tro",
        store=True
    )

    @api.depends('thoi_gian_bat_dau', 'thoi_gian_ket_thuc')
    def _compute_ngay_ho_tro(self):
        for record in self:
            if record.thoi_gian_bat_dau and record.thoi_gian_ket_thuc:
                delta = record.thoi_gian_ket_thuc - record.thoi_gian_bat_dau
                record.ngay_ho_tro = delta.total_seconds() / 86400.0  # Chia cho số giây trong 1 ngày
            else:
                record.ngay_ho_tro = 0

    # Yêu cầu & mô tả
    yeu_cau_cua_khach = fields.Text(string="Yêu cầu của khách hàng")
    mo_ta_chi_tiet = fields.Text(string="Mô tả chi tiết")

    # Trạng thái xử lý
    trang_thai = fields.Selection([
        ('pending', 'Đang chờ'),
        ('in_progress', 'Đang xử lý'),
        ('resolved', 'Đã giải quyết')
    ], string="Trạng thái", default='pending')

    nhan_vien_phu_trach = fields.Many2one(
        'nhan.vien',
        string="Nhân viên phụ trách",
    )

    # Phản hồi & đánh giá từ khách hàng
    phan_hoi_khach_hang = fields.Text(string="Phản hồi của khách hàng")
    diem_danh_gia = fields.Integer(string="Điểm đánh giá từ khách hàng", default=0)

    # File đính kèm
    file_dinh_kem = fields.Many2many(
        'ir.attachment',
        'ho_tro_khach_hang_attachment_rel',
        'ho_tro_khach_hang_id',
        'attachment_id',
        string="File đính kèm"
    )

    # Ràng buộc dữ liệu: Điểm đánh giá phải từ 0 đến 5
    _sql_constraints = [
        ('check_diem_danh_gia', 'CHECK(diem_danh_gia BETWEEN 0 AND 5)',
         'Điểm đánh giá phải từ 0 đến 5!')
    ]

    @api.constrains('trang_thai', 'thoi_gian_ket_thuc', 'diem_danh_gia')
    def _check_thoi_gian_va_diem_danh_gia(self):
        for record in self:
            if record.trang_thai != 'resolved' and (record.thoi_gian_ket_thuc or record.diem_danh_gia):
                raise ValidationError(
                    "Chỉ được nhập thời gian kết thúc và điểm đánh giá khi trạng thái là 'Đã giải quyết'!")

    @api.model
    def create(self, vals):
        record = super(HoTroKhachHang, self).create(vals)
        # Cập nhật thống kê sau khi tạo bản ghi mới
        self.env['thong_ke_ho_tro_nhan_vien'].update_thong_ke()
        # Tự động tạo task từ ticket
        record._auto_tao_task()
        return record

    def _auto_tao_task(self):
        """Tự động tạo task tương ứng khi có ticket hỗ trợ mới"""
        priority_map = {
            'thap': '0',
            'trung_binh': '1',
            'cao': '2',
            'khan_cap': '3',
        }
        deadline_days = {
            'thap': 7,
            'trung_binh': 3,
            'cao': 1,
            'khan_cap': 0,  # Hôm nay
        }
        muc_uu_tien = self.muc_do_uu_tien or 'trung_binh'
        ngay_deadline = fields.Date.today() + timedelta(days=deadline_days.get(muc_uu_tien, 3))

        self.env['task'].create({
            'name': f"[{self.ma_ho_tro}] {self.yeu_cau_cua_khach or 'Hỗ trợ khách hàng'}",
            'description': self.mo_ta_chi_tiet or '',
            'priority': priority_map.get(muc_uu_tien, '1'),
            'khach_hang_id': self.ten_khach_hang.id,
            'ho_tro_khach_hang_id': self.id,
            'deadline': ngay_deadline,
            # leader_id để trống → Gemini tự phân công
        })

    def write(self, vals):
        result = super(HoTroKhachHang, self).write(vals)
        if 'nhan_vien_phu_trach' in vals:
            self.env['thong_ke_ho_tro_nhan_vien'].update_thong_ke(self)
        return result

    def unlink(self):
        nhan_vien_ids = self.mapped('nhan_vien_phu_trach').ids
        result = super(HoTroKhachHang, self).unlink()
        if nhan_vien_ids:
            self.env['thong_ke_ho_tro_nhan_vien'].update_thong_ke(nhan_vien_ids)
        return result
