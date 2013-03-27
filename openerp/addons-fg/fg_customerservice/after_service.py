#!/usr/bin/env python
# -*- coding: utf-8 -*-

from osv import osv, fields
from tools.translate import _
import time




class after_service(osv.osv):
	_name = 'after.service'
	_description = '售后支持'
	_inherit = ['mail.thread']
	
	#def write(self, cr, uid, ids, data, context={}):
	#	result = super(after_service, self).write(cr, uid, ids, data, context=context)
	#	cases = self.browse(cr, uid, ids)
	#	self.message_append(cr, uid, cases, _('修改'))
	#	return result
	
	def create(self, cr, uid, vals, context={}):
		result = super(after_service, self).create(cr, uid, vals, context=context)
		cases = self.browse(cr, uid, result)
		self.message_append(cr, uid, [cases], _('创建'))
		return result
		
		
	
	_columns = {
		'date':fields.date('创建日期', readonly=True),
		
		'contact_name':fields.char('退件人姓名', size=64, required=True, readonly=True, states={'draft':[('readonly',False)]} ),
		 
		'tel':fields.char('联系电话', size=64, readonly=True, states={'draft':[('readonly',False)]}),
		
		'address':fields.char('退件人地址', size=128, readonly=True, states={'draft':[('readonly',False)]}),
		
		'receive_num':fields.char('退件单号', size=64,  readonly=True, states={'draft':[('readonly',False)]}),
		
		'receiver':fields.many2one('res.users', '收件人', required=True, readonly=True, states={'draft':[('readonly',False)]}),
		
		'receive_product':fields.char('退件产品',size=64,readonly=True, states={'draft':[('readonly',False)]}),
		
		'commit_to':fields.many2one('res.users', '交给', readonly=True, states={'processig':[('readonly',False)]}),
		
		'product_name':fields.many2one('fuguang.picking.item', '产品名称', readonly=True, states={'draft':[('readonly',False)]}),
		
		'quality_reason':fields.text('质量原因', size=256, help='客户反映的质量问题', readonly=True, states={'draft':[('readonly',False)]}),
		
		'identify':fields.text('质量处鉴定', size=256, readonly=True, states={'processing':[('readonly',False)]}),
		
		'solve':fields.char('处理意见', size=256, help='填写您的处理意见', readonly=True, states={'processing':[('readonly',False)]}),
		
		'in_charge':fields.many2one('res.users', '负责人', readonly=True),
		
		'return_num':fields.char('回件单号', size=64, readonly=False, states={'draft':[('readonly',True)]} ,help='问题分析解决后可调换产品给退件人'),
		
		'returner':fields.many2one('res.users', '回件人姓名', readonly=False, states={'draft':[('readonly',True)]},help='问题分析解决后可调换产品给退件人'),
		
		'return_product':fields.char('回件产品',size=64,readonly=False, states={'draft':[('readonly',True)]}),
		
		'salse_head':fields.many2one('res.users', '销售负责人鉴定', size=64, ),
		
		'related_department':fields.selection([(u'FGA事业部',u'FGA事业部'),(u'塑胶事业部',u'塑胶事业部'), (u'安全帽事业部',u'安全帽事业部'), 
			(u'玻璃事业部',u'玻璃事业部'), (u'真空事业部',u'真空事业部'),(u'塑胶制品',u'塑胶制品'), (u'财务部',u'财务部'),
			(u'其他',u'其他')],'相关事业部', readonly=True, states={'draft':[('readonly',False)]}),
		
		'state': fields.selection([('draft', '投诉'), ('processing', '处理中'), ('cancelled','取消'), ('done','已解决')], '处理情况', readonly=True),
		
		'message_ids': fields.one2many('mail.message', 'res_id', 'Messages', domain=[('model','=',_name)]),
		
		'pic':fields.binary('照片',help='问题产品照片'),
		
		'return_date':fields.date('回件日期', readonly=False, states={'draft':[('readonly',True)]}),
	}

	_defaults = {
		'date':fields.date.context_today,
		'receiver':lambda obj, cr, uid, context: uid,
		'state':lambda *a:'draft',
		'in_charge':lambda obj,cr,uid,context: uid,
	}	
	
	def case_draft(self, cr, uid, ids, *args):
		cases = self.browse(cr, uid, ids)
		self.message_append(cr, uid, cases, _('将状态给为新投诉'))
		self.write(cr, uid, ids, {'state': 'draft'})
		return True
	def case_cancelled(self, cr, uid, ids, *args):
		cases = self.browse(cr, uid, ids)
		self.message_append(cr, uid, cases, _('将投诉取消'))
		self.write(cr, uid, ids, {'state': 'cancelled'})
		return True
	def case_processing(self, cr, uid, ids, *args):
		cases = self.browse(cr, uid, ids)
		self.message_append(cr, uid, cases, _('将新投诉递交处理流程'))
		self.write(cr, uid, ids,{'state': 'processing'})
		return True
	def case_done(self, cr, uid, ids, *args):
		cases = self.browse(cr, uid, ids)
		suggestion=self.read(cr, uid, ids, ['solve'], context={})
		if suggestion[0]['solve']:
			suggestmessage = '处理意见为：' + str(suggestion[0]['solve'])
			self.message_append(cr, uid, cases,_(suggestmessage))
		self.message_append(cr, uid, cases, _('投诉处理完成可调换新产品给顾客'))
		self.write(cr, uid, ids, {'state': 'done'})
		return True
	
after_service()	

	

	

	
	

	
	
