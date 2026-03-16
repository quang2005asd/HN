# -*- coding: utf-8 -*-
from odoo import models, fields, api


class NguoiNhan(models.Model):
    _name = 'nguoi.nhan'
    _description = 'Người nhận văn bản'

    name = fields.Char("Họ tên", required=True)
    chuc_vu = fields.Char("Chức vụ")
    phong_ban = fields.Char("Phòng ban")
    email = fields.Char("Email")
    so_dien_thoai = fields.Char("Số điện thoại")
    active = fields.Boolean("Kích hoạt", default=True)
