# -*- coding: utf-8 -*-
{
    'name': "Quản Lý Văn Bản",

    'summary': """
        Hệ thống quản lý văn bản đến và văn bản đi""",

    'description': """
        Module quản lý văn bản bao gồm:
        - Văn bản đến
        - Văn bản đi
        - Loại văn bản
        - Người nhận
        - Log hoạt động
        - Phiếu chuyển
        - Báo cáo
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    'category': 'Productivity',
    'version': '0.1',

    'depends': ['base', 'mail'],

    'data': [
        'security/ir.model.access.csv',
        'views/loai_van_ban.xml',
        'views/van_ban_den.xml',
        'views/van_ban_di.xml',
        'views/nguoi_nhan.xml',
        'views/log_hoat_dong.xml',
        'views/phieu_chuyen.xml',
        'views/bao_cao.xml',
        'views/menu.xml',
    ],

    'demo': [],
    'installable': True,
    'application': True,
}
