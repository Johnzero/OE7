# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    'name': 'Portal HighCharts',
    'version': '0.1',
    'category': 'Tools',
    'complexity': 'easy',
    'description': """
This module adds HighCharts menu and features to your portal .
==========================================================================================
    """,
    'author': 'Xero',
    'depends': ['portal'],
    'data': [
        'highcharts_view.xml',
    ],
    'installable': True,
    'auto_install': True,
    'category': 'Hidden',
    "js":[
          "static/src/js/highcharts.js",
          "static/src/js/exporting.js",
          "static/src/js/demo.js",
        ],
    "css":[],
    #'qweb': ['static/src/xml/HighCharts.xml'],
    'images':[],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
