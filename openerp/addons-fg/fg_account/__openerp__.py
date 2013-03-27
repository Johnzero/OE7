# encoding: utf-8

# 
# Copyright (c) 2012 Daniel Yang. All rights reserved.
# 
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
# 
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
# 
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
{
    "name": "富光财务",
    "version": "1.0",
    "depends": ["base","fg_sale","mail"],
    'author': 'Daniel',
    'website': 'http://www.ide.fm',
    'category' : '富光',
    "description": """
       富光财务基本模块.
       """,
    "init_xml": [],
    'update_xml': [
        'security/group.xml',
        'security/ir.model.access.csv',
        "fg_account.xml",
        'report/period_check_view.xml',
        "wizard/wizard.xml",
        "wizard/customer.xml",
        'data.xml'
    ],
    'demo_xml': [],
    'installable': True,
    'active': True,
    'application':True,
}