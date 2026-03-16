# -*- coding: utf-8 -*-
from odoo import models, fields, api


class LoaiVanBan(models.Model):
    _name = 'loai.van.ban'
    _description = 'Loại văn bản'

    name = fields.Char("Tên loại văn bản", required=True)
    ma_loai = fields.Char("Mã loại", required=True)
    mo_ta = fields.Text("Mô tả")
    active = fields.Boolean("Kích hoạt", default=True)
