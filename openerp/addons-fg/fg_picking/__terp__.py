# -*- encoding: utf-8 -*-

{
    'name': '富光出库单',
    'version': '1.1',
    'category' : '富光',
    'description': """富光出库单""",
    'author': 'Daniel',
    'website': 'http://www.ide.fm',
    'depends': ['base', 'mail', 'fg_data'],
    'init_xml': [],
    'update_xml': [
		'security/user.xml',
		'security/ir.model.access.csv',
        'picking_sequence.xml',
        'picking_views.xml',
        'wizard/wizard.xml',
		# 'data/items.xml',
		#'data/1st_cus_20120424.xml',
		#'data/category.xml',
		#'data/customer.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
    'application':True,
}