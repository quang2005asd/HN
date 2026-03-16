# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ThongTinKhachHangExtend(models.Model):
    _inherit = 'thong_tin_khach_hang'
    
    # Không dùng One2many để tránh lỗi inverse, dùng compute thay thế
    task_count = fields.Integer("Số công việc", compute='_compute_task_count')
    task_dang_thuc_hien = fields.Integer("Công việc đang thực hiện", compute='_compute_task_stats')
    task_hoan_thanh = fields.Integer("Công việc hoàn thành", compute='_compute_task_stats')
    
    def _compute_task_count(self):
        for record in self:
            record.task_count = self.env['task'].search_count([('khach_hang_id', '=', record.id)])
    
    def _compute_task_stats(self):
        for record in self:
            record.task_dang_thuc_hien = self.env['task'].search_count([('khach_hang_id', '=', record.id), ('state', '=', 'in_progress')])
            record.task_hoan_thanh = self.env['task'].search_count([('khach_hang_id', '=', record.id), ('state', '=', 'done')])
    
    def action_view_tasks(self):
        """Hiển thị danh sách công việc của khách hàng"""
        return {
            'name': 'Công việc',
            'type': 'ir.actions.act_window',
            'res_model': 'task',
            'view_mode': 'tree,form',
            'domain': [('khach_hang_id', '=', self.id)],
            'context': {'default_khach_hang_id': self.id}
        }
