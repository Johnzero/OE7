{
    "name": "富光网络渠道管理",
    "version": "1.0",
    "depends": ["base","mail"],
    'author': '杨振宇，汪松',
    'website': 'http://www.fuguang.cn',
    'category' : '富光',
    "description": """
       富光网络渠道管理模块.
       """,
    "init_xml": [],
    'update_xml': [
        'security/group.xml',
        'security/ir.model.access.csv',
        'online_shop_view.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
    'application':True,
    'auto_install': False,
    'js':['static/src/js/fg_onlineshop.js']
}