# -*- coding: utf-8 -*-

from osv import fields, osv
from ..taobao_top import TOP
from ..taobao_top import TOPException
from openerp.loglevels import ustr
import logging

_logger = logging.getLogger(__name__)
class taobao_delivery_update_line(osv.osv_memory):
    _name = "taobao.delivery.update.line"
    _description = "Taobao Delivery Stock Update Line"
    _columns = {
            'delivery_ref': fields.char(u'发货单号', size = 64,readonly = 1),
            'tid': fields.char(u'淘宝单号', size = 64,readonly = 1),
            'carrier_tracking_ref': fields.char(u'运单号', size = 64,readonly = 1),
            'company_code': fields.char(u'物流公司代码', size = 64,readonly = 1),
            'taobao_shop_id': fields.many2one('taobao.shop', 'Taobao Shop'),
            'wizard_id' : fields.many2one('taobao.delivery.update', string="Wizard"),
            }

class taobao_delivery_update(osv.osv_memory):
    _name = "taobao.delivery.update"
    _description = "Taobao Delivery Update"
    _columns = {
            'delivery_update_lines' : fields.one2many('taobao.delivery.update.line', 'wizard_id', u'订单列表'),
            }

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(taobao_delivery_update, self).default_get(cr, uid, fields, context=context)
        active_model = context.get('active_model', False)
        active_ids = context.get('active_ids', False)

        delivery_update_lines = []
        if active_model == 'stock.picking.out' and active_ids:
            for taobao_delivery_obj in self.pool.get('stock.picking.out').browse(cr, uid, active_ids, context=context):
                sale_obj = False
                sale_id = False
                tids = []
                if taobao_delivery_obj.origin:
                    sale_id = self.pool.get('sale.order').search(cr,uid,[('name','=',taobao_delivery_obj.origin)])
                if not sale_id: continue
                sale_obj = self.pool.get('sale.order').browse(cr,uid,sale_id[0])
                shop_ids = self.pool.get('taobao.shop').search(cr,uid,[('name','=',sale_obj.shop_id.name)])
                shop_id = shop_ids and shop_ids[0] or 1
                tids = sale_obj.origin and sale_obj.origin.split(',')
                if sale_obj.name[0:4] == 'TBMG' and len(tids) > 1: # 是淘宝合并单（发货地址相同）
                    if not taobao_delivery_obj.carrier_id:continue
                    for tid in tids:
                        delivery_update_lines.append({
                            'delivery_ref': taobao_delivery_obj.name,
                            'tid' : tid,
                            'carrier_tracking_ref' : taobao_delivery_obj.carrier_tracking_ref,
                            'company_code' : taobao_delivery_obj.carrier_id and taobao_delivery_obj.carrier_id.code,
                            'taobao_shop_id': shop_id,
                        })
                else:
                    if not sale_obj.taobao_trade_id:continue
                    if not taobao_delivery_obj.carrier_id:continue
                    delivery_update_lines.append({
                        'delivery_ref': taobao_delivery_obj.name,
                        'tid' : sale_obj and sale_obj.taobao_trade_id or '',
                        'carrier_tracking_ref' : taobao_delivery_obj.carrier_tracking_ref,
                        'company_code' : taobao_delivery_obj.carrier_id and taobao_delivery_obj.carrier_id.code,
                        'taobao_shop_id': shop_id,
                    })

        context['delivery_update_lines'] = delivery_update_lines
        if 'delivery_update_lines' in fields and context.has_key('delivery_update_lines'):
            res.update({'delivery_update_lines': context['delivery_update_lines']})
        return res

    def update_delivery(self, cr, uid, ids, context=None):
        err_res = ""
        for delivery_update_obj in self.browse(cr, uid, ids, context=context):
            res = ""
            for line in delivery_update_obj.delivery_update_lines:
                shop = self.pool.get('taobao.shop').browse(cr,uid,line.taobao_shop_id.id)
                top = TOP(shop.taobao_app_key, shop.taobao_app_secret, shop.taobao_session_key)
                if not line.carrier_tracking_ref:
                    res += u"发货单号：%s，淘宝单号：%s 该单没有运单号。\n"%(line.delivery_ref,line.tid)
                    continue
                try:
                    tao_res = self.pool.get('stock.picking.out')._top_item_deliver_update(top, line.carrier_tracking_ref, line.tid, company_code = line.company_code)
                except TOPException,e:
                    res += u"发货单号：%s，淘宝单号：%s 发货错误[%s] \n" % (line.delivery_ref,line.tid,ustr(e))

            if res:err_res = "" + res
        if not err_res:
            return {'type': 'ir.actions.act_window_close',}
        else:
            raise osv.except_osv(u'出错单列表:',err_res)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
