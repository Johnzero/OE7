# -*- encoding: utf-8 -*-
import pooler, time
from osv import fields, osv
from tools import get_initial


class sale_shop(osv.osv):
    _name = "fg_sale.shop"
    _description = "富光销售机构"
    _columns = {
        'name': fields.char('机构名称', size=64, required=True),
        'pricelist_id': fields.many2one('product.pricelist', '价格表'),
        'company_id': fields.many2one('res.company', '公司', required=False),
    }
    _defaults = {
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'fg_sale.shop', context=c),
    }

class sale_order(osv.osv):
    _name = "fg_sale.order"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "富光业务部销售订单"
    
    
    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = { 'amount_total':0.0 }
            amount = 0
            for line in order.order_line:
                #todo: got to decide which one to add. subtotal_amount or, discount_amount
                amount = amount + line.subtotal_amount
            res[order.id]['amount_total'] = amount
        return res
    
    def _amount_discount(self, cr, uid, ids, field_name, arg, context=None):
        
        res = {}
        product_obj = self.pool.get('product.product')
        
        #discount.
        for order in self.browse(cr, uid, ids, context=context):
            
            discount = 0
            for line in order.order_line:
                product = product_obj.browse(cr, uid, line.product_id.id, context=context)
                d = product.list_price * line.aux_qty - line.subtotal_amount
                
                discount = discount + d
            res[order.id] = { 'amount_discount':discount }
        return res
    
    _columns = {
        'name': fields.char('单号', size=64, select=True, readonly=True),
        'sub_name': fields.char('副单号', size=64, select=True, readonly=True),
        'date_order': fields.date('日期', required=True, readonly=True, select=True, states={'draft': [('readonly', False)]}),
        'date_confirm': fields.date('审核日期', readonly=True, select=True),
        
        'user_id': fields.many2one('res.users', '制单人', select=True, readonly=True),
        'confirmer_id': fields.many2one('res.users', '审核人', select=True, readonly=True),
        'partner_id': fields.many2one('res.partner', '客户', readonly=True, states={'draft': [('readonly', False)]}, required=True, change_default=True),
        #关联id错误
        'partner_shipping_id': fields.many2one('res.partner', '送货地址', readonly=True, states={'draft': [('readonly', False)]}, required=False, change_default=True, select=True),
        'amount_total': fields.function(_amount_all, string='金额', store=True, multi='sums'),
        'amount_discount': fields.function(_amount_discount, string='折扣', store=False, multi='sums'),
        'order_line': fields.one2many('fg_sale.order.line', 'order_id', '订单明细', readonly=True, states={'draft': [('readonly', False)]}),
        'state': fields.selection([('draft', '未审核'), ('done', '已审核'), ('cancel','已取消')], '订单状态', readonly=True, select=True),
        'minus': fields.boolean('红字', readonly=True, states={'draft': [('readonly', False)]}),
        'note': fields.char('摘要', size=64, readonly=True, states={'draft': [('readonly', False)]}),
        'promotion':fields.boolean('促销', readonly=True, states={'draft': [('readonly', False)]}),
    }
        
    _defaults = {
        'date_order': fields.date.context_today,
        'state': 'draft',
        'minus': False, 
        'promotion': False,
        'user_id': lambda obj, cr, uid, context: uid,
        'partner_shipping_id': lambda self, cr, uid, context: context.get('partner_id', False) and self.pool.get('res.partner').address_get(cr, uid, [context['partner_id']], ['default'])['default'],
    }
    
    def copy(self, cr, uid, id, default={}, context=None):
        raise osv.except_osv('不允许复制', '订单不允许复制.')
    
    def create(self, cr, uid, vals, context=None):
        if not vals.has_key('name'):
            obj_sequence = self.pool.get('ir.sequence')
            vals['name'] = obj_sequence.get(cr, uid, 'fg_sale.order')
            
        if not vals.has_key('sub_name'):
            partner_obj = self.pool.get('res.partner')
            partner_name = partner_obj.name_get(cr, uid, [vals['partner_id']])[0][1]
            initial = get_initial(partner_name)
            
            cr.execute("select count(*) from fg_sale_order where partner_id = %s;" % vals['partner_id'] )
            res = cr.fetchone()
            count = res and res[0] or 0
            
            vals['sub_name'] = "FGSO-%s-%s" % ( initial, count+1 )
            print vals,'vals'

        return super(sale_order, self).create(cr, uid, vals, context)

    def button_review(self, cr, uid, ids, context=None):
        
        product_obj = self.pool.get('product.product')
        order_line_obj = self.pool.get('fg_sale.order.line')
        orders = self.browse(cr, uid, ids)
        for order in orders:
            for line in order.order_line:
                if order.minus:
                    # set lines to minus.
                    
                    update = {
                            'product_uom_qty':(0-line.product_uom_qty),
                            'aux_qty':(0-line.aux_qty),
                            'subtotal_amount':(0-line.subtotal_amount),
                        }
                    order_line_obj.write(cr, uid, [line.id], update)
                        
                    self.message_post(cr, uid,
                                [order.id],
                                body='业务单据 <b>%s</b> 为红单。'% order.name,
                                subtype='fg_sale.mt_order_red',
                                context=context)

            if order.amount_discount > 0:
                self.message_post(cr, uid,
                        [order.id],
                        body='业务单据 <b>%s</b> 中存在折扣。'% order.name,
                        subtype='fg_sale.mt_order_discount',
                        context=context)
        
        self.write(cr, uid, ids, { 
            'state': 'done', 
            'confirmer_id': uid, 
            'date_confirm': fields.date.context_today(self, cr, uid, context=context),
            }
        )
        return True
    
    def button_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, { 
            'state': 'cancel', 
            'confirmer_id': uid, 
            'date_confirm': fields.date.context_today(self, cr, uid, context=context),
            }
        )
        
        return True
    
    def button_dummy(self, cr, uid, ids, context=None):
        return True
    
    
    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        if not part:
            return {'value': {'partner_shipping_id': False}}
        part = self.pool.get('res.partner').browse(cr, uid, part, context=context)
        if part.parent_id and not part.is_company:
            part = part.parent_id
        
        addr = self.pool.get('res.partner').address_get(cr, uid, [part.id], ['default', 'delivery', 'contact'])
        #dedicated_salesman = part.user_id and part.user_id.id or uid
        val = {
            'partner_shipping_id': addr['default'],
            #'user_id': dedicated_salesman,
        }
        return {'value': val}
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', '订单名称不能重复!'),
    ]
    _order = 'id desc'
    
class sale_order_line(osv.osv):
    _name = "fg_sale.order.line"
    _description = "富光业务部销售订单明细"
    
    _columns = {
        'order_id': fields.many2one('fg_sale.order', '订单', required=True, ondelete='cascade', select=True),
        'sequence': fields.integer('Sequence'),
        'product_id': fields.many2one('product.product', '产品', required=True, domain=[('sale_ok', '=', True)], change_default=True),
        'product_uom': fields.many2one('product.uom', ' 单位', required=True),
        'product_uom_qty': fields.float('数量', required=True, digits=(16,4)),
        'aux_qty': fields.float('只数', required=True, digits=(16,4)),
        'unit_price': fields.float('单价', required=True, digits=(16,4)),
        'subtotal_amount': fields.float('小计', digits=(16,4)),
        'note': fields.char('附注', size=100),
    }
    
    _defaults={
    }
    
    
    def product_id_change(self, cr, uid, ids, product_id, context=None):
        if not product_id:
            return {'domain': {}, 'value':{'product_uom':'', 'product_uom_qty':0, 
                'aux_qty':0, 'unit_price':0, 'subtotal_amount':0}}
        result = {}
        product_obj = self.pool.get('product.product')
        product_uom_obj = self.pool.get('product.uom')
        
        product = product_obj.browse(cr, uid, product_id, context=context)
        
        uom_list = [product.uom_id.id, 11, 22]
        # uoms = product_uom_obj.search(cr, uid, [('uom_type','=','smaller'), ('category_id','=',1)])
        #         for u in uoms:
        #             uom_list.append(u)

        domain = {'product_uom':[('id','in',uom_list)]}

        result['product_uom'] = product.uom_id.id
        result['unit_price'] = product.lst_price
        
        return {'domain':domain, 'value': result}
    
    
    def product_uom_id_change(self, cr, uid, ids, product_id, uom_id, context=None):
        return {'domain': {}, 'value':{'product_uom_qty':0, 
            'aux_qty':0, 'subtotal_amount':0}}
    
    
    def product_uom_qty_change(self, cr, uid, ids, product_id, product_uom, qty, unit_price_new, context=None):
        if product_id and product_uom and qty and unit_price_new:
            product_obj = self.pool.get('product.product')
            product_uom_obj = self.pool.get('product.uom')
            product = product_obj.browse(cr, uid, product_id, context=context)
            
            uom = product_uom_obj.browse(cr, uid, product_uom)
            
            factor = uom and uom.factor or 1
            
            if product:
                price = unit_price_new * factor * qty
                
                return {'value': {'subtotal_amount':price, 'aux_qty':factor * qty}}
        return {'value':{}}
    

    _order = 'sequence, id asc'