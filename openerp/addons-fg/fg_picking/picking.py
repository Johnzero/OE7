# -*- encoding: utf-8 -*-

from osv import osv
from osv import fields
import time

class res_partner(osv.osv):
	_inherit = 'res.partner'
	_columns = {
	'client_id': fields.many2one('res.users', '登录账号', help='客户登录系统的账号'),
	}
	
res_partner()

class picking_item_color(osv.osv):
    _name = 'fuguang.picking.item.color'
    _description = '产品颜色'
    _rec_name = 'color'
    
    _columns = {
        'item_id': fields.many2one('fuguang.picking.item', '产品', required=True, ondelete='cascade', select=True),
        'color': fields.char('颜色', size=20, required=True),
        'sequence': fields.float('序号', digits=(8, 1)),
    }
    
    _order = 'sequence asc'

class picking_uom(osv.osv):
    _name = 'fuguang.picking.item.uom'
    _description = '产品计量单位'
    
    _columns = {
        'name': fields.char('名称', size=40, required=True),
        'factor':fields.float('换算率', digits=(8, 1)),
    }
picking_uom()

class picking_item(osv.osv):
    _name = 'fuguang.picking.item'
    _description = '产品'
    _rec_name = 'code'
    
    # def _get_available(self, cr, uid, ids, name, arg, context=None):
    #      group_ids = self.pool.get('res.groups').search(cr, uid, [('name', 'in', ('富光 / 客户'))])
    #      items = self.pool.get('fuguang.picking.item').browse(cr, uid, ids, context)
    #      
    
    _columns = {
        'name': fields.char('名称', size=40, required=True),
        'category': fields.char('事业部', size=40, required=True),
        'code':fields.char('货号', size=20, required=True),
        'barcode':fields.char('条码', size=20),
        'price':fields.float('单品价格', digits=(8, 2)),
        'uoms': fields.many2many('fuguang.picking.item.uom', 'rel_picking_uom','picking_item_id','uom_id', '计量单位'),
        'sequence': fields.float('序号', digits=(8, 1)),
        'colors':fields.one2many('fuguang.picking.item.color', 'item_id', '颜色', ondelete='cascade'),
        'state': fields.selection([('presale', '预售'), ('sale', '在售'), ('expiring', '即将停产'), ('expired', '已停产')], '状态'),
        'user_ids': fields.many2many('res.users', 'rel_picking_item_user','picking_item_id','user_id', '可见客户'),
        'volume':fields.char('体积', size=40),
    }
    
    def name_get(self, cr, uid, ids, context=None):
        res = []
        for r in self.read(cr, uid, ids, ['code','name']):
            res.append((r['id'], '%s (%s)' % (r['code'], r['name'])))

        return res

    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        name = name.upper()
        if not args:
            args=[]
        if name:
            ids = self.search(cr, user, [('code','=',name)]+ args, limit=limit, context=context)
            if not len(ids):
                ids = self.search(cr, user, ['|',('name',operator,name),('code',operator,name)] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, user, args, limit=limit, context=context)
        result = self.name_get(cr, user, ids, context=context)
        return result
    
    _defaults = {
        'state': lambda obj, cr, uid, context: 'sale',
    }
    
    _sql_constraints = [
           ('item_sequence_uniq', 'unique(sequence)', '序号不能重复.'),
    ]
    
    _order = 'sequence asc'

picking_item()
picking_item_color()

class fg_order(osv.osv):
    
    _name = 'fuguang.order'
    _description = '富光客户订单'
    _rec_name = 'name'
    
    
    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = { 'total_amount':0.0 }
            amount = 0
            for line in order.order_line:
                amount = amount + line.amount
            res[order.id]['total_amount'] = amount
        return res
    
    _columns = {
        'name': fields.char('编号', size=64, readonly=True),
        'date_order': fields.date('开单日期', required=True, readonly=True),
        'user_id': fields.many2one('res.users', '创建人', readonly=True),
        'partner_id': fields.many2one('res.partner', '客户', readonly=True),
        'partner_address_id': fields.many2one('res.partner.address', '送货地址', required=True, readonly=True), 
        'total_amount': fields.function(_amount_all, method=True, string='总价', multi='sums'),
        'order_line': fields.one2many('fuguang.order.line', 'order_id', '订单明细'),
        'notifier_ids': fields.many2many('res.users', 'rel_order_user','order_id','user_id', '可见客户'),
        'sales_ids': fields.related('partner_id','sales_ids', type='many2many', relation='res.users', string='负责人',store=False),
        'note':fields.text('附注'),
    }
    
    def _default_partner(self, cr, uid, context=None):
        
        cr.execute("""
        SELECT id, client_id
          FROM res_partner
          where client_id = %s;
        
        """ % uid)
        res = cr.fetchone()
                
        return res and res[0] or False
    
    def _default_partner_address(self, cr, uid, context=None):
        cr.execute("""
        SELECT id, client_id
          FROM res_partner
          where client_id = %s;
        
        """ % uid)
        res = cr.fetchone()
        partner = res and res[0] or False
        if not partner: return False;
        
        partner_obj = self.pool.get('res.partner')
        addr = partner_obj.address_get(cr, uid, [partner], ['default'])['default']
        return addr
    
    def _default_name(self, cr, uid, context=None):
        name = self.pool.get('ir.sequence').get(cr, uid, 'fuguang.order')
        return name
        
    _defaults = {
        'date_order': lambda *a: time.strftime('%Y-%m-%d'),
        'user_id': lambda obj, cr, uid, context: uid,
        #'name': _default_name,
        'partner_id': _default_partner, 
        'partner_address_id': _default_partner_address,
    }
    
    
    def create(self, cr, uid, vals, context=None):
        if not vals.has_key('name'):
            obj_sequence = self.pool.get('ir.sequence')
            vals['name'] = obj_sequence.get(cr, uid, 'fuguang.order')
        
        id = super(fg_order, self).create(cr, uid, vals, context)
        
        #notify:
        cr.execute("""
        SELECT id, client_id
          FROM res_partner
          where client_id = %s;
        
        """ % uid)
        res = cr.fetchone()
        
        if res:
            body = """
            %s 您好! 
            这是一封提醒邮件. 
            客户 %s 已经于 %s 在订单系统里创建了一个编号为 %s 的订单.
            请及时处理.
            """
            
            partner_id = res[0]
            mail_message = self.pool.get('mail.message')
            partner_obj = self.pool.get('res.partner')
        
            partner = partner_obj.browse(cr, uid, [partner_id], context=context)
            for p in partner:
                mail_to = [ user.user_email for user in p.sales_ids if user.active and user.user_email ]
                user_names = [ user.name for user in p.sales_ids if user.active ]
                if None not in mail_to:
                        mail_message.schedule_with_attach(cr, uid,
                            '富光ERP系统 <fuguang_fg@163.com>',
                            mail_to + ['133120528@qq.com'],
                            '[订单提醒]编号:%s' % vals['name'],
                            body % (','.join(user_names), p.name, time.strftime('%Y-%m-%d %H:%m'),vals['name']),
                            reply_to='fuguang_fg@163.com',
                            context=context
                        )

        return id

    def copy(self, cr, uid, id, default={}, context=None):
        raise osv.except_osv('不允许复制', '订单不允许复制.')
    
    _order = 'name desc'
    
fg_order()

class fg_order_line(osv.osv):
    _name = 'fuguang.order.line'
    _description = '富光客户订单明细'
    
    _columns = {
        'order_id': fields.many2one('fuguang.order', 'Order Reference', required=True, ondelete='cascade', select=True),
        'barcode':fields.char('条码', size=20),
        'product_id': fields.many2one('fuguang.picking.item', '产品', required=True),
        'qty': fields.float('数量', digits=(16, 0), required=True),
        'product_uom': fields.many2one('fuguang.picking.item.uom', '单位', required=True),
        'color': fields.many2one('fuguang.picking.item.color', '颜色', required=True),
        'amount': fields.float('价格', digits=(8, 2)),
        'notes': fields.char('附注', size=20),
    }
    
    _order = 'id desc'
    
    # def _get_products(self, cr, uid, context=None):
    #     """
    #     get products.
    #     """
    #     items = self.pool.get('res.users').browse(cr, uid, uid, context=context)
    # 
    # _defaults = {
    #     'product_id':_get_products,
    # }
    
    def product_id_change(self, cr, uid, ids, product_id):
        if not product_id:
            return {'domain': {}, 'value':{'product_uom':'', 'color':'', 'qty':0, 'amount':0}}
        
        # warning = {
        #             'title': '测试 !',
        #             'message':
        #                 '测试一下 !\n'
        #                 '本产品即将停售.'
        #             }
        # get uom
        item_obj = self.pool.get('fuguang.picking.item')
        item = item_obj.browse(cr, uid, product_id)
        uom_list = [u.id for u in item.uoms]
        value = {'product_uom':uom_list[-1]}

        domain = {'color':[('item_id','=',product_id)], 'product_uom':[('id','in',uom_list)]}
        return {'domain': domain, 'value':value} # 'warning': warning}

    def product_uom_change(self, cr, uid, ids, product_id, product_uom):
        return {'value': {'qty':0, 'amount':0}}

    def qty_change(self, cr, uid, ids, product_id, product_uom, qty):
        amount = 0        
        if product_id and product_uom and qty:
            product_obj = self.pool.get('fuguang.picking.item')
            product = product_obj.browse(cr, uid, [product_id])
            if product:
                price = product[0].price
                uom_obj = self.pool.get('fuguang.picking.item.uom')
                uom = uom_obj.browse(cr, uid, [product_uom])
                if uom:
                    factor = uom[0].factor
                    amount = factor * price * qty
        return {'value':{'amount': amount}}


fg_order_line()

class fg_delivery(osv.osv):
    _name = 'fuguang.delivery'
    _description = '仓库发货单'
    
    _columns = {
        'name': fields.char('单号', size=64, required=True, readonly=True),
        'partner_name': fields.char('发货单位', size=64, required=True),
        'dep_name': fields.char('事业部', size=64),
        'date_import':fields.date('开单日期'),
        'user_id': fields.many2one('res.users', '下单人', readonly=True),
        'lines': fields.one2many('fuguang.delivery.line', 'delivery_id', '明细'),
    }
    
    def create(self, cr, uid, vals, context=None):
        if not vals.has_key('name'):
            obj_sequence = self.pool.get('ir.sequence')
            vals['name'] = obj_sequence.get(cr, uid, 'fuguang.delivery')
        
        id = super(fg_delivery, self).create(cr, uid, vals, context)
        return id
    
    _defaults = {
        'user_id': lambda obj, cr, uid, context: uid,
        'date_import': fields.date.context_today,
    }
    
    _order = 'name desc'
    
class fg_delivery_line(osv.osv):
    _name = 'fuguang.delivery.line'
    _description = '仓库发货单明细'
    
    _columns = {
        'delivery_id':fields.many2one('fuguang.delivery', 'Delivery Reference', required=True, ondelete='cascade', select=True),
        'product':fields.char('品名', size=64, required=True),
        'code':fields.char('货号', size=64),
        'color':fields.char('颜色', size=64),
        'uom':fields.char('单位', size=64),
        'plan':fields.char('计划发出', size=64),
        'real':fields.char('实际发出', size=64),
        'warehouse':fields.char('货物所在地', size=64),
        'note':fields.char('备注', size=128),
    }
