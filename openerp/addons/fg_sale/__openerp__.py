# -*- encoding: utf-8 -*-

{
    'name': '富光销售模块',
    'version': '2.0',
    'category' : '富光',
    'description': """销售模块""",
    'author': '杨振宇',
    'website': 'http://www.fuguang.cn',
    'depends': ['base', 'board', 'product', 'fg_base'],
    'init_xml': [],
    'update_xml': [
        'fg_sale_data.xml',
        'security/group.xml',
        'security/ir.model.access.csv',
        'fg_sale_view.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
    'application':True,
}