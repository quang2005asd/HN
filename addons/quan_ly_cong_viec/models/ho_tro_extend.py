# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HoTroKhachHangExtend(models.Model):
    _inherit = 'ho_tro_khach_hang'
    
    task_lien_quan_count = fields.Integer("Số công việc liên quan", compute='_compute_task_count')
    
    def _compute_task_count(self):
        for record in self:
            record.task_lien_quan_count = self.env['task'].search_count([('ho_tro_khach_hang_id', '=', record.id)])
    
    def action_tao_task_tu_ticket(self):
        """Tạo task từ ticket hỗ trợ"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tạo công việc',
            'res_model': 'task',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_name': f"Hỗ trợ: {self.yeu_cau_cua_khach or 'N/A'}",
                'default_khach_hang_id': self.ten_khach_hang.id,
                'default_ho_tro_khach_hang_id': self.id,
                'default_leader_id': self.nhan_vien_phu_trach.id,
                'default_description': self.mo_ta_chi_tiet,
            }
        }
    
    def action_view_tasks_lien_quan(self):
        """Xem các task liên quan đến ticket này"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Công việc liên quan',
            'res_model': 'task',
            'view_mode': 'tree,form',
            'domain': [('ho_tro_khach_hang_id', '=', self.id)],
        }
