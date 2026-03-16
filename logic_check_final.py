from odoo import fields
from datetime import datetime

kh = env['thong_tin_khach_hang'].search([('vung_mien','=','trung')], limit=1)
if not kh:
    print('NO_KH_TRUNG')
else:
    ticket = env['ho_tro_khach_hang'].create({
        'ten_khach_hang': kh.id,
        'muc_do_uu_tien': 'cao',
        'phuong_thuc_lien_lac': 'email',
        'thoi_gian_bat_dau': fields.Datetime.now(),
        'yeu_cau_cua_khach': f'Logic Check {datetime.now().strftime("%Y%m%d%H%M%S")}',
        'mo_ta_chi_tiet': 'Logic check final',
    })
    task = env['task'].search([('ho_tro_khach_hang_id','=',ticket.id)], order='id desc', limit=1)
    print('TICKET=', ticket.ma_ho_tro)
    print('KH_VUNG=', kh.vung_mien)
    print('LEADER=', task.leader_id.name if task and task.leader_id else None)
    print('LEADER_VUNG=', task.leader_id.vung_mien if task and task.leader_id else None)
    print('PRIORITY=', task.priority if task else None)
