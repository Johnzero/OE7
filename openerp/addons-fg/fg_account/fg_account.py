# -*- encoding: utf-8 -*-

from osv import osv
from osv import fields
import time
import tools

class sale_order(osv.osv):
    _inherit = "fg_sale.order"
    
    _columns = {
        'reconciled':fields.boolean('已对账'),
        'clear':fields.boolean('已清账'),
    }
    
    _defaults = {
        'reconciled':False,
        'clear':False,
    }
    

class account_bill_category(osv.osv):
    _name = "fg_account.bill.category"
    _description = "收款单分类"

    _columns = {
        'code':fields.char('代号', size=64, select=True, required=True),
        'name': fields.char('名称', size=64, select=True, required=True),
    }

class account_bill(osv.osv):
    _name = "fg_account.bill"
    _description = "收款单"

    _columns = {
        'name': fields.char('单号', size=64, select=True, readonly=True),
        'user_id': fields.many2one('res.users', '录入', select=True, readonly=True),
        'date_paying': fields.date('收款日期', select=True, readonly=True),
        'checker_id': fields.many2one('res.users', '检查人', required=False, select=True, readonly=True),
        'date_check': fields.date('检查日期',readonly=False, required=False, states={'done': [('readonly', True)]}, select=True),
        'category_id':fields.many2one('fg_account.bill.category', '分类', required=True,readonly=False, states={'done': [('readonly', True)]}, select=True),
        'partner_id': fields.many2one('res.partner', '客户', readonly=False, states={'done': [('readonly', True)]}, select=True),
        'amount': fields.float('金额', digits=(16,4),required=True,readonly=False, states={'done': [('readonly', True)]},),
        'state': fields.selection([('draft', '未检查'), ('check', '已检查'), ('done', '已审核'), ('cancel','已作废')], '订单状态', readonly=True, select=True),
        'reconciled':fields.boolean('已对账'),
        'note': fields.text('附注', readonly=False, states={'done': [('readonly', True)]},),
    }

    _defaults = {
        'date_paying': fields.date.context_today,
        'state': 'draft',
        'user_id': lambda obj, cr, uid, context: uid,
        'reconciled':False,
    }
    
    _order = "name desc"
    
    def copy(self, cr, uid, id, default={}, context=None):
        raise osv.except_osv('不允许复制', '单据不允许复制.')
    
    def create(self, cr, uid, vals, context=None):
        if not vals.has_key('name'):
            obj_sequence = self.pool.get('ir.sequence')
            vals['name'] = obj_sequence.get(cr, uid, 'fg_account.bill')
        
        return super(account_bill, self).create(cr, uid, vals, context)
    
    #钱总确认.
    def button_done(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, { 
            'state': 'done', 
            }
        )
        return True
    
    def button_check(self, cr, uid, ids, context=None):
        
        bill_ids = []
        for bill in self.browse(cr, uid, ids, context):
            if not bill['partner_id']:
                bill_ids.append(bill['name'])
        if bill_ids:
            raise osv.except_osv('未确认客户的单据', '以下单据还没有确认用户: %s' % ','.join(bill_ids))
        
        self.write(cr, uid, ids, { 
            'state': 'check', 
            'checker_id': uid, 
            'date_check': fields.date.context_today(self, cr, uid, context=context),
            }
        )

        return True
    
    
    def button_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, { 
            'state': 'cancel', 
            'checker_id': uid, 
            'date_check': fields.date.context_today(self, cr, uid, context=context),
            }
        )
        return True