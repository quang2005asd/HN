# quan_ly_cong_viec/models/task.py
from odoo import models, fields, api

class Task(models.Model):
    _name = 'task'
    _description = 'Công việc'
    _inherit = ['mail.thread']

    name = fields.Char(string="Tên công việc", required=True)
    description = fields.Text(string="Mô tả")
    deadline = fields.Date(string="Ngày hết hạn")
    priority = fields.Selection([
        ('0', 'Thấp'),
        ('1', 'Bình thường'),
        ('2', 'Cao'),
        ('3', 'Khẩn cấp'),
    ], string="Mức độ ưu tiên", default='1', required=True)
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('in_progress', 'Đang thực hiện'),
        ('done', 'Hoàn thành'),
    ], string="Trạng thái", default='draft')
    
    # Liên kết với khách hàng
    khach_hang_id = fields.Many2one('thong_tin_khach_hang', string="Khách hàng", help="Khách hàng liên quan đến công việc này")
    ho_tro_khach_hang_id = fields.Many2one('ho_tro_khach_hang', string="Ticket hỗ trợ", help="Liên kết với yêu cầu hỗ trợ khách hàng")
    
    # Liên kết với nhân viên
    leader_id = fields.Many2one('nhan.vien', string="Trưởng nhóm")
    member_ids = fields.Many2many('nhan.vien', string="Thành viên")
    
    progress = fields.Float(string="Tiến độ (%)", default=0.0, help="Phần trăm hoàn thành công việc (0-100%)")
    attachment_ids = fields.One2many('ir.attachment', 'res_id', string="Tệp đính kèm", domain=[('res_model', '=', 'task')])
    my_task_ids = fields.One2many('my_task', 'task_id', string="Công việc cá nhân")

    @api.onchange('progress')
    def _onchange_progress(self):
        for task in self:
            if task.progress >= 100:
                task.state = 'done'
            elif task.progress > 0 and task.state == 'draft':
                task.state = 'in_progress'

    def _get_assigned_tasks(self):
        current_employee = self.env['nhan.vien'].search([('user_id', '=', self.env.user.id)], limit=1)
        if current_employee:
            return self.search(['|', ('leader_id', '=', current_employee.id), ('member_ids', 'in', current_employee.id)])
        return self.env['task']

    @api.model
    def create(self, vals):
        # Nếu không có leader → gọi Gemini phân công tự động
        gemini_ly_do = None
        if not vals.get('leader_id'):
            nhan_vien_id, ly_do = self._auto_assign_with_gemini(vals)
            if nhan_vien_id:
                vals['leader_id'] = nhan_vien_id
                gemini_ly_do = ly_do

        task = super(Task, self).create(vals)
        task._update_my_tasks()

        # Log lý do phân công vào chatter
        if gemini_ly_do and task.leader_id:
            task.message_post(
                body=f"🤖 <b>Gemini AI tự động phân công:</b> {task.leader_id.name}<br/>"
                     f"<i>{gemini_ly_do}</i>",
                message_type='comment',
                subtype_xmlid='mail.mt_note',
            )

        return task

    @api.model
    def _auto_assign_with_gemini(self, vals):
        """Thu thập context và gọi Gemini AI để chọn leader phù hợp"""
        nhan_viens = self.env['nhan.vien'].search([])
        if not nhan_viens:
            return None, "Không có nhân viên nào trong hệ thống"

        # Build danh sách NV với workload hiện tại
        nv_list = []
        for nv in nhan_viens:
            nv_list.append({
                'id': nv.id,
                'name': nv.name,
                'vung_mien': nv.vung_mien or '',
                'task_count': nv.task_count,
                'luong_co_ban': nv.luong_co_ban,
            })

        # Build thông tin task
        task_info = {
            'name': vals.get('name', ''),
            'description': vals.get('description', ''),
            'priority': str(vals.get('priority', '1')),
            'deadline': str(vals.get('deadline', '')) if vals.get('deadline') else None,
        }

        # Thêm thông tin khách hàng nếu có
        if vals.get('khach_hang_id'):
            kh = self.env['thong_tin_khach_hang'].browse(vals['khach_hang_id'])
            task_info['khach_hang'] = kh.ten_khach_hang
            task_info['vung_mien_kh'] = kh.vung_mien or ''

        nhan_vien_id, ly_do = self.env['gemini.ai.service'].phan_cong_nhan_vien(task_info, nv_list)

        # Ràng buộc cứng theo vùng miền ở tầng code (trừ task khẩn cấp)
        if nhan_vien_id and task_info.get('priority') != '3' and task_info.get('vung_mien_kh'):
            vung_mien_kh = task_info.get('vung_mien_kh')
            selected_nv = next((nv for nv in nv_list if nv['id'] == nhan_vien_id), None)
            same_region_nvs = [nv for nv in nv_list if nv.get('vung_mien') == vung_mien_kh]

            if same_region_nvs and (not selected_nv or selected_nv.get('vung_mien') != vung_mien_kh):
                best_same_region = min(same_region_nvs, key=lambda x: x['task_count'])
                nhan_vien_id = best_same_region['id']
                ly_do = f"{ly_do} | Điều chỉnh ưu tiên cùng vùng miền khách hàng"

        return nhan_vien_id, ly_do

    def write(self, vals):
        res = super(Task, self).write(vals)
        self._update_my_tasks()
        return res

    def _update_my_tasks(self):
        self.my_task_ids.unlink()
        if self.leader_id and self.leader_id.user_id:
            self.env['my_task'].create({
                'task_id': self.id,
                'user_id': self.leader_id.user_id.id,
                'assigned_role': 'leader',
                'name': self.name,
                'description': self.description,
                'deadline': self.deadline,
                'progress': self.progress,
            })
        for member in self.member_ids:
            if member.user_id:
                self.env['my_task'].create({
                    'task_id': self.id,
                    'user_id': member.user_id.id,
                    'assigned_role': 'member',
                    'name': self.name,
                    'description': self.description,
                    'deadline': self.deadline,
                    'progress': self.progress,
                })

    @api.model
    def _init_my_tasks(self):
        tasks = self.search([])
        for task in tasks:
            task._update_my_tasks()