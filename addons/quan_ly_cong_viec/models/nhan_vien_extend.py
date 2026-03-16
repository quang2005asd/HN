# -*- coding: utf-8 -*-
from odoo import models, fields, api


class NhanVienExtend(models.Model):
    _inherit = 'nhan.vien'
    
    # Không dùng One2many để tránh lỗi inverse, dùng compute thay thế
    task_count = fields.Integer("Số công việc", compute='_compute_task_count')
    khach_hang_phu_trach_count = fields.Integer("Số KH phụ trách", compute='_compute_khach_hang_count')
    
    def _compute_task_count(self):
        for record in self:
            leader_count = self.env['task'].search_count([('leader_id', '=', record.id)])
            member_count = self.env['task'].search_count([('member_ids', 'in', record.id)])
            record.task_count = leader_count + member_count
    
    def _compute_khach_hang_count(self):
        for record in self:
            record.khach_hang_phu_trach_count = self.env['thong_tin_khach_hang'].search_count([('nhan_vien_phu_trach_id', '=', record.id)])
    
    def action_view_cong_viec(self):
        """Hiển thị danh sách công việc của nhân viên"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Công việc',
            'res_model': 'task',
            'view_mode': 'tree,form',
            'domain': ['|', ('leader_id', '=', self.id), ('member_ids', 'in', self.id)],
            'context': {'default_leader_id': self.id}
        }
    
    def action_view_khach_hang_phu_trach(self):
        """Hiển thị danh sách khách hàng mà nhân viên phụ trách"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Khách hàng phụ trách',
            'res_model': 'thong_tin_khach_hang',
            'view_mode': 'tree,form',
            'domain': [('nhan_vien_phu_trach_id', '=', self.id)],
            'context': {'default_nhan_vien_phu_trach_id': self.id}
        }
