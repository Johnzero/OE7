# -*- coding: utf-8 -*-

from openerp.osv import osv, fields
from openerp import SUPERUSER_ID
import PyWapFetion

class feitionsetting(osv.TransientModel):

    _inherit = 'base.config.settings'
    _description = "Fetion Setting"

    _columns = {
        "fetion" : fields.char('账号',size = 64,readonly=False,help="飞信登陆手机号"),
        "key" : fields.char("密码",size = 64,readonly=False),
    }
    
    _defaults = {
        "fetion" : "13956070164",
        "key" : "wangsong1233276",
    }

class fetion(osv.osv):

    _name = "fetion"
    _inherit = "mail.compose.message"
    _columns = {

    }
    
    def send_fetion_message(self, cr, uid, ids, context=None):

    
        return True
    
    def send_myself_fetion_message(self, cr, uid, ids, context=None):

        pass


