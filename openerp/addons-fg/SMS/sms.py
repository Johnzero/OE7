# -*- coding: utf-8 -*-

from openerp.osv import osv, fields,orm
from openerp import SUPERUSER_ID
import PyWapFetion
from PyWapFetion import Fetion

class feitionsetting(osv.TransientModel):

    _inherit = 'base.config.settings'
    _description = "Fetion Setting"

    def create(self, cr, uid, vals, context={}):

        config_parameter_obj = self.pool.get("ir.config_parameter")
        
        config_parameter_obj.set_param(cr, uid, "fetion",vals["fetion"])
        config_parameter_obj.set_param(cr, uid, "key",vals["key"])
        return super(feitionsetting, self).create(cr, uid, vals, context=context)
    
    def get_default_fetion(self, cr, uid, ids, context=None):

        config_parameter_obj = self.pool.get("ir.config_parameter")
        fetion = config_parameter_obj.get_param(cr, uid, "fetion", context=context)
        key = config_parameter_obj.get_param(cr, uid, "key", context=context)
        return {'fetion' : fetion,'key' : key}

    _columns = {
        "fetion" : fields.char('账号',size = 64,readonly=False,help="飞信登陆手机号"),
        "key" : fields.char("密码",size = 64,readonly=False),
    }
    
    _defaults = {
        "fetion" : "13956070164",
        "key" : "zero1233276",
    }

class fetion(osv.osv):

    _name = "fetion"
    _inherit = "mail.compose.message"
    _columns = {

        'fetion_partner': fields.many2many('res.partner',
            'phone_compose_message_res_partner_rel',
            'wizard_id', 'partner_id', '联系人',change_default=True,required=True),
        "fetion_message":fields.text(u"消息",required=True),

    }
    _defaults = {
        "fetion_message":"test",
    }
    
    def default_get(self, cr, uid, fields, context=None):
        
        result = super(fetion, self).default_get(cr, uid, fields, context=context)
        config_parameter_obj = self.pool.get("ir.config_parameter")
        fetion_username = config_parameter_obj.get_param(cr, uid, "fetion", context=context)
        key = config_parameter_obj.get_param(cr, uid, "key", context=context)
        global myfetion
        try:
            myfetion = Fetion(fetion_username, key)
        except:return result
        print myfetion
        return result
    
    def on_change_partner(self, cr, uid, ids, res_id, fetion_partner, context=None):
        
        if res_id[0][-1]:
            res_partner = self.pool.get("res.partner")
            partner = res_partner.browse(cr, uid,res_id[0][-1][-1],context=None)
            if partner.mobile:
                answer = myfetion.findid(partner.mobile)
                if not answer:
                    del res_id[0][-1][-1]
                    return {'value': {'fetion_partner': res_id}}
        else:return True
        return True
    
    def send_fetion_message(self, cr, uid, ids, context=None):
        
        fields = self.browse(cr, uid, ids[0], context=context)
        if fields.fetion_message:message = fields.fetion_message
        for partner in fields.fetion_partner:
            answer = myfetion.send(partner.mobile, message, sm=True)
            if not answer:answer = myfetion.send(partner.mobile, message, sm=True)
            if not answer:
                raise osv.except_osv(u"发送飞信失败", u"请联系管理员!")
        return True
    
    def send_myself_fetion_message(self, cr, uid, ids, context=None):

        pass


