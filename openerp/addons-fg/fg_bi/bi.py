#!/usr/bin/env python
# -*- coding: utf-8 -*-

from osv import osv, fields
from tools.translate import _
import time,datetime
import re,json
from os import path as op

class bi_product(osv.osv):
	
	_name = 'bi_product'
	_description = 'Business Intelligence'
	
	_columns = {
		
		'name':fields.many2one('product.product', 'Name',),
		'code':fields.char('Code',size=64),
		'system':fields.char('System',size=64),
		'date':fields.datetime('Date'),
		'product_id':fields.integer('Product Id'),
		'aux_qty':fields.integer('Aux Q'),
		'year':fields.char('Year',size=64),
		'month':fields.char('Month',size=64),
		'qty':fields.integer('Q'),
		'padding':fields.integer('Padding'),
		'source':fields.char('Source',size=64),
		'purpose':fields.char('Purpose',size=64),
		
	}
	
	_defaults = {

	}
	
	def query(self, cr, uid, ids, context={}):
		if self.read(cr,uid, ids, ['name'])[0]['name']:
			pid = self.read(cr,uid, ids, ['name'])[0]['name'][0]
		else:return True
		cr.execute('SELECT create_date,subtotal_amount FROM fg_sale_order_line WHERE product_id=%s ORDER BY create_date',(pid,));
		data = cr.fetchall();
		jsondict = [];
		reg = '(.*?)\s'
		for da in data:
		    d = re.findall(reg,da[0])
		    d = time.mktime(time.strptime(d[0],"%Y-%m-%d"))*1000
		    d = int("%.0f" % d)
		    try:
			for js in jsondict:
				if js and js[0] == d :
				    js[1]+=da[1]
				    raise NameError()
		    except NameError:pass	
	            else:jsondict.append([d,da[1]])
		jsondict = json.dumps(jsondict)
		path = op.abspath('.')+'\\openerp'+'\\addons'+'\\web\\static\\src\\data.json'
		file = open(path,'w')
		file.write(jsondict)
		file.close()
		return True

	def updateModule(self, cr, uid, ids, context={}):
	    mod_obj = self.pool.get('ir.module.module')
	    ids = mod_obj.search(cr, uid, [('name','=',self._module)])
	    mod_obj.button_upgrade(cr, uid, ids)
	    objs = self.pool.get('base.module.upgrade')
	    objs.upgrade_module(cr, uid, ids, context=None)
	    return True
	
bi_product()
