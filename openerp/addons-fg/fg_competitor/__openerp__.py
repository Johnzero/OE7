# -*- encoding: utf-8 -*-

{
    'name': '竞争对手分析',
    'version': '1.0',
    'category' : '富光',
    'description': """富光竞争对手分析子系统""",
    'author': '杨振宇',
    'website': 'http://www.fuguang.cn',
    'depends': ['base', 'board'],
    'init_xml': [],
    'update_xml': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'competitor.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
    'application':True,
    'css':['static/src/css/competitor.css']
}