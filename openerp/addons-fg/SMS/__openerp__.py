# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2011 OpenERP s.a. (<http://openerp.com>).
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
    'name': 'Fetion Short Message Service',
    'version': '2.0',
    'category': 'Tools',
    'description': """
Fetion Short Message Service in the web client.
===========================================================

    """,
    'author': 'OpenERP SA',
    'website': 'http://openerp.com',
    'depends': ["base",'base_setup',"mail"],
    'js' : ["static/src/js/sms.js"],
    "update_xml" : [
        "sms.xml",
    ],
    'css' : ["static/src/css/sms.css"],
    'qweb' : ["static/src/xml/sms.xml"],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
