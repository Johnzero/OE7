# -*- coding: utf-8 -*-

from openerp.osv import osv, fields
from openerp import SUPERUSER_ID
import PyWapFetion
from PyWapFetion import Fetion

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

        'fetion_partner': fields.many2many('res.partner',
            'phone_compose_message_res_partner_rel',
            'wizard_id', 'partner_id', '联系人'),

    }
    
    def send_fetion_message(self, cr, uid, ids, context=None):

        base_module = self.pool.get("base.config.settings")
        print ids

        fetion_list = base_module.read(cr, uid, [1], ["fetion","key"],context=None)

        print fetion_list

        if not fetion_list[0]["fetion"]:return True

        myfetion = Fetion(fetion_list[0]["fetion"], fetion_list[0]["key"])


        return True
    
    def send_myself_fetion_message(self, cr, uid, ids, context=None):

        pass


