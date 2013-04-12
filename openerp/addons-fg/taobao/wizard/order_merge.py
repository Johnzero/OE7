# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP Module
#    
##############################################################################
from osv import osv, fields
from tools.translate import _
import netsvc
import logging

class sale_order_merge_wizard(osv.osv_memory):
    _name = "sale.order.merge.wizard"
    _description = u"合并发货地址相同的淘宝订单"
    
    def merge_so(self, cr, uid, ids,context=None):
        sale_obj = self.pool.get('sale.order')
        order_line_obj = self.pool.get('sale.order.line')
        sale_orders = []
        active_ids = context.get('active_ids',[])
        ship_name = False
        min_pay_date = False
        min_pay_date_so = False
        if len(active_ids)<2:
            raise osv.except_osv(_('Warning'),_('Please select multiple order to merge in the list view.'))
        for so in sale_obj.browse(cr, uid,active_ids,context):
            if so.state == 'done' or so.state == 'cancel' or so.shipped or so.invoiced:
                raise osv.except_osv(_('Warning'), _('You can not merge sale order in Done or Cancelled state !'))
            ctx = {'show_address':1}
            key = self.pool.get('res.partner').name_get(cr, uid, [so.partner_shipping_id.id],ctx)[0][1]
            if not ship_name:ship_name = key
            elif ship_name <> key:
                raise osv.except_osv(_('Warning'), _('You can not merge sale order with different shipping address !'))
            if not min_pay_date:
                min_pay_date = so.taobao_pay_time
                min_pay_date_so = so
            if min_pay_date < so.taobao_pay_time:
                min_pay_date_so = so
            sale_orders.append(so)
            
        so_name = self.pool.get('ir.sequence').get(cr, uid, 'so.merge_type')
        merge_so={
            'name': so_name,
            'origin':','.join(map(lambda x:x.taobao_trade_id,sale_orders)),
            'date_order': min_pay_date_so and min_pay_date_so.date_order or False,
            'state': 'draft',
            'shop_id':min_pay_date_so and min_pay_date_so.shop_id and min_pay_date_so.shop_id.id or False,
            'partner_id':min_pay_date_so and min_pay_date_so.partner_id.id or False,
            #'partner_order_id':min_pay_date_so and min_pay_date_so.partner_order_id and min_pay_date_so.partner_order_id.id or False,
            'partner_invoice_id':min_pay_date_so and min_pay_date_so.partner_invoice_id and min_pay_date_so.partner_invoice_id.id or False,
            'partner_shipping_id':min_pay_date_so and min_pay_date_so.partner_shipping_id and min_pay_date_so.partner_shipping_id.id or False,
            'pricelist_id':min_pay_date_so and min_pay_date_so.pricelist_id.id or False,
        }
        so_id = sale_obj.create(cr, uid, merge_so)
        for so in sale_orders:
            for ln in so.order_line:
                vals = {
                    'order_id':so_id,
                    'product_id':ln.product_id.id or False,
                    'name':ln.name or '',
                    'product_uom_qty':ln.product_uom_qty or 1.00,
                    'product_uom':ln.product_uom.id or False,
                    'price_unit':ln.price_unit or 0.00,
                    'product_packaging':ln.product_packaging and product_packaging.id or False,
                    'discount':ln.discount or 0.00,
                    'type':ln.type or False,
                    'delay':ln.delay or False,
                }
                order_line_obj._save(cr, uid,**vals)
                
            sale_obj._taobao_cancel_order(self.pool,cr,uid,[so.id])
        return {'type': 'ir.actions.act_window_close'}

sale_order_merge_wizard()

