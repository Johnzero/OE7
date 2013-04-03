# -*- encoding: utf-8 -*-
from osv import fields, osv
    
class res_partner(osv.osv):
    _inherit = 'res.partner'
    _columns = {
        'fullnum': fields.char('num', size=40),
        'sales_ids': fields.many2many('res.users', 'rel_partner_user','partner_id','user_id', '负责业务员', help='内部负责业务员. 设置邮件地址,以备通知使用.'),
    }


class res_user(osv.osv):
    _inherit = 'res.users'
    _columns = {
        'jid': fields.char('num', size=40),
        'partner_ids':fields.many2many('res.partner', 'rel_partner_user', 'user_id', 'partner_id', '负责客户', help='负责客户'),
    }

class product_uom(osv.osv):
    _inherit = 'product.uom'
    _columns = {
        'fullnum': fields.char('num', size=40),
        
    }

class product_product(osv.osv):
    _inherit = 'product.product'
    _columns = {
        'fullnum': fields.char('num', size=40),
        'source':fields.selection([(u'塑胶事业部',u'塑胶事业部'), (u'安全帽事业部',u'安全帽事业部'), 
                (u'玻璃事业部',u'玻璃事业部'), (u'茶叶事业部',u'茶叶事业部'),(u'真空事业部',u'真空事业部'),(u'塑胶制品',u'塑胶制品'), (u'财务部',u'财务部'),
                (u'其他',u'其他')],'事业部', required=True),
    }
    
class product_category(osv.osv):
    _inherit = 'product.category'
    _columns = {
        'fullnum': fields.char('num', size=40),
    }
    
class fg_report_horizontal(osv.osv_memory):
    _name = "fg_data.report.horizontal"

    _columns = {
        'name':fields.char('项目', size=40),
        'desc':fields.char('说明', size=40),
        'value': fields.float('数据', digits=(12, 2)),
    }