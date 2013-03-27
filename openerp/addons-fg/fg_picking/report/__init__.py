# -*- encoding: utf-8 -*-

from report import report_sxw
from osv import osv
import tools

class order_html(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(order_html, self).__init__(cr, uid, name, context)
        
        #get pick item obj
        picking_item_obj = self.pool.get('fuguang.picking.item')
        item_ids = picking_item_obj.search(cr, uid, [])
        result = []
        for item in picking_item_obj.browse(cr, uid, item_ids):
            data = {
                'category': item.category,
                'name': item.name,
                'code':item.code,
                'colors':[]
            }
            for c in item.colors:
                data['colors'].append(c.color)
            
            result.append(data)
        
        
        self.localcontext.update({
            'picking_items':result,
        })

class picking_html(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(picking_html, self).__init__(cr, uid, name, context)

report_sxw.report_sxw('report.fuguang.order.html','fuguang.order',
    'addons/fg_picking/report/order.html',parser=order_html)


report_sxw.report_sxw('report.fuguang.picking.html','fuguang.delivery',
    'addons/fg_picking/report/picking.html',parser=picking_html)