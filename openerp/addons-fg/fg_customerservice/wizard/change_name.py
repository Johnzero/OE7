#!/usr/bin/env python
# -*- coding: utf-8 -*-

from osv import osv, fields
from tools.translate import _
import time




class change_name(osv.osv_memory):
	_name = 'changename'
	_description = 'chang responsible person'
	
	def change_to(self, cr, uid, ids, context=None):
		
		'''更改负责人'''
		
		obj=self.pool.get('after.service')
		service_id = context.get('active_ids')
		cases = obj.browse(cr, uid, service_id)
		commit=self.read(cr, uid, ids, ['commit_to'], context={})
		suggestion=obj.read(cr, uid, service_id, ['solve'], context={})
		
		if not suggestion[0]['solve']:
			raise osv.except_osv(_('Warning !'), _('请填写处理意见'))
		else:
			suggestmessage = '处理意见为：' + str(suggestion[0]['solve'])
			obj.message_append(cr, uid, cases,_(suggestmessage))
		
		time.sleep(0.6)
		
		if not commit[0]['commit_to']:
			return {'type': 'ir.actions.act_window_close'}
		else:
			name=commit[0]['commit_to'][1]
			commitid=commit[0]['commit_to'][0]
			val = '将处理意见提交给' + name
			obj.message_append(cr, uid, cases, _(val))
			cr.execute('UPDATE after_service SET commit_to=null,solve=null,in_charge=%s where id in %s',(commitid,tuple(service_id)))
			cr.commit()
			
			#send mail
			objuser= self.pool.get('res.users')
			mailto = objuser.read(cr, uid, commitid, ['user_email'], context=None)
			if not mailto["user_email"]:
				pass
				#raise osv.except_osv(_('Warning !'), _('该负责邮件地址不存在，请及时提醒处理！'))
			else:
				body = """
				
				您好, ! 
				这是一封提醒邮件.
				您有新的投诉问题需要处理！, 请及时查看售后服务模块.
				
				"""
				mail_message = self.pool.get('mail.message')
				msg_id = mail_message.schedule_with_attach(cr, uid,
				    'wangsong@fuguang.cn',
				    [mailto["user_email"]],
				    '[您有新的投诉问题需要处理！]',
				    body = body,
				    reply_to='fuguang_fg@163.com',
				    context=context)
				res = mail_message.send(cr, uid, [msg_id], auto_commit=True, context=context)
		
		return {'type': 'ir.actions.act_window_close'}
	
	
	
		
	_columns = {
		'in_charge':fields.many2one('res.users', '负责人', readonly=True),
		
		'commit_to':fields.many2one('res.users', '交给'),
		
		'date':fields.date("日期",readonly=True)
	}

	_defaults = {
		'in_charge':lambda obj,cr,uid,context: uid,
		
		'date':fields.date.context_today,

	}
	
change_name()