# -*- encoding: utf-8 -*-

{
    'name': '物料推进',
    'version': '1.0',
    'category' : '富光',
    'description': """产 品 物 料 推 进 表""",
    'author': '',
    'website': 'http://www.fuguang.cn',
    'depends': ['base','hr'],
    'init_xml': [],
    'update_xml': [
        "security/group.xml",
        'security/ir.model.access.csv',
        'fg_schedule.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
    'application':True,
    'css':['']
}