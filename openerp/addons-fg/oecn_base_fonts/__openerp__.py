# -*- encoding: utf-8 -*-
# __author__ = tony@openerp.cn
##############################################################################
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
#
##############################################################################
{
    "name" : "pdf report support for your language",
    "version" : "2.1",
    "author" : "Shine IT",
    "maintainer":"jeff@openerp.cn",
    "website": "http://www.openerp.cn",
    "description": """
    Fonts defined in the default report may not support characters
    in your language, which may cause jarbled characters in the printed
    pdf report.
    
    This addon will solve abovementioned issue elegently by using openerp
    customfonts API to replace the original fonts with your seleted fonts.

    Please click open Settings/Configuration/Configuration Wizards/Configuration Wizards
    click the launch buttong(gear icon) on the line of 'Configure fonts mapping for pdf report'
    
    set up the font mapping from the poped window there and
    
    have fun!
    ---------Tips-----------
    1.when you restore the database to another system, please run the configuration wizards again.
    """,
    "depends" : ["base",'base_setup'],
    "category" : "Generic Modules/Base",
    "demo_xml" : [],
    "update_xml" : [
        "res_config_view.xml"
        ],
    "license": "GPL-3",
    "active": False,
    "auto_install":True,
    "installable": True
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

