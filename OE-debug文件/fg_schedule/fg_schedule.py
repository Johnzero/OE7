# -*- encoding: utf-8 -*-

import pooler, time, base64
from osv import fields, osv

AVAILABLE_PRIORITIES = [
    ('1', '最高'),
    ('2', '高'),
    ('3', '中'),
    ('4', '低'),
    ('5', '最低'),
]
class fg_jobcontent(osv.osv):
    
    _name = "fg_jobcontent"
    _description = u"工作项目进度表"
    
    _columns = {

        'name': fields.char('项目名称', size=128, select=True, required=True,),
        
        "executor": fields.many2one('res.users','执行人', required=True, select=True,),
        
        'charge':fields.char('下单人', size=128,),
        
        "date_start":fields.date("下单时间",required=False,),
        
        "date_end":fields.date("实际完成时间",),
        
        'note': fields.text('备注',size=512),
        
        "accept": fields.char('对接人',size=128,),
        
        "explain":fields.text('说明(要求)',),
        
        "rate":fields.text('工作进度',),
        
        "end_time": fields.date('要求完成时间',),
        
        'jobstate': fields.selection([('draft', '未开始'),('processing','进行中'),('done','已完成')], '状态',),
        
    }
    
    _defaults = {
                'date_start':fields.date.context_today,
                'executor':lambda obj, cr, uid, context: uid,
                'jobstate':'draft',
		}

class task(osv.osv):
    
    _name = "fg_project.task"
    _description = u"产品物料推进任务"
    
    def _get_img(self, cr, uid, ids, name, arg, context=None):
        
        res = {}
        image = None
        eid = self.read(cr, uid, ids, ['executor'])
        cr.execute('SELECT id FROM resource_resource WHERE user_id = %s', (eid[0]["executor"][0],))
        reid = cr.fetchone()
        obj = self.pool.get("resource.resource")
        objhr = self.pool.get("hr.employee")
        if reid:
            cr.execute('SELECT image FROM hr_employee WHERE resource_id = %s', (reid[0],))
            image = cr.fetchone()
        if image :image = image[0]
        res[ids[0]]= image
        
        return res
      
    _columns = {
        
        'name': fields.char('任务',select=True, required=True, size=128 ),
        
	'color': fields.integer('Color Index'),
	
        "project": fields.many2one('fg_schedule.project','项目',select=True, required=True, ),
        
        "executor": fields.many2one('res.users','执行人', required=True, select=True),
        
        "executor_img": fields.function(_get_img, method=True, string='头像', type='binary', store=True, ),
        
        "order": fields.char('下单人',size=128, select=True),
        
        "order_time": fields.date('下单时间', ),
        
        'detil': fields.text('工作摘要',size=512, ),
        
        "need_endtime": fields.date('截止时间'),
        
        "end_time": fields.date('完成时间',readonly=True, ),
        
        "accept": fields.char('对接人',size=128, ),
        
        'state': fields.selection([('draft', '未开始'), ('processing', '执行中'), ('cancelled','取消（删除）'), ('done','完成')], '推进情况',required=True),
        
        "explain":fields.text('项目说明(要求)', ),
        
        "rate":fields.float('项目进度',),
        
        "note": fields.text('备注',),
        
        'img':fields.binary("效果展示",readonly=True,),
        
        #-------------------------------------------------------
        'colour':fields.one2many('product.colour', 'colour_schedule', '产品颜色'),
        
        'barcode':fields.one2many('bar.code', 'barcode', '条形码申报'),
        
        'productbook':fields.one2many('product.book', 'book_schedule', '产品说明书'),
        
        'colorboard':fields.one2many('color.board', 'colorboard', '色板确认'),
        
        'accessorypurchaser':fields.one2many('accessory.purchaser', 'accessorypurchaser', '辅料采购'),
        
        'screenmaking':fields.one2many('screen.making', 'screenmaking', '网版制作'),
        
        'productsample':fields.one2many('product.sample', 'productsample', '产品打样'),
        
        'productpack':fields.one2many('product.pack', 'productpack', '产品包装'),
        
        'productshoot':fields.one2many('product.shoot', 'productshoot', '产品拍摄及修图'),
        
        'producttag':fields.one2many('product.tag', 'producttag', '吊牌,插卡,标签'),
        
        'productopp':fields.one2many('product.opp', 'productopp', 'OPP袋,低压袋'),
        
        'productcontainer':fields.one2many('product.container', 'productcontainer', '产品外箱'),
        
        'productposter':fields.one2many('product.poster', 'productposter', '海报'),
        
        'productelse':fields.one2many('product.else', 'productelse', '其他'),
        
    }
    
    _defaults = {
    'need_endtime':fields.date.context_today,
    'order_time':fields.date.context_today,
    'state':'draft',
    'rate':0.00,
    'color':0,
    'executor':lambda obj, cr, uid, context: uid,
    }

    def case_draft(self, cr, uid, ids, *args):
	self.write(cr, uid, ids, {'state': 'draft','end_time':False, 'rate':0})
	return True
    def case_processing(self, cr, uid, ids, *args):
	self.write(cr, uid, ids, {'state': 'processing','end_time':False, 'rate':0})
	return True
    def case_done(self, cr, uid, ids, *args):
	self.write(cr, uid, ids, {'state': 'done','end_time':time.strftime("%Y-%m-%d %H:%M:%S"),'rate':100})
	return True    
    def button(self, cr, uid, ids, *args):
        return True
    
task()

class project(osv.osv):
    
    _name = "fg_schedule.project"
    _description ="fg_schedule.project"
    
    def create(self, cr, uid, vals, context={}):
	result = super(project, self).create(cr, uid, vals, context=context)
        print result,'------------'
	obj = self.pool.get('fg_project.task')
        obj.create(cr, uid, {'name':'产品颜色','project':result,'executor':uid,'state':'draft','need_endtime':None}, context=context)
	obj.create(cr, uid, {'name':'条形码申报','project':result,'executor':uid,'state':'draft','need_endtime':None}, context=context)
        obj.create(cr, uid, {'name':'产品说明书','project':result,'executor':uid,'state':'draft','need_endtime':None}, context=context)
        obj.create(cr, uid, {'name':'色板确认','project':result,'executor':uid,'state':'draft','need_endtime':None}, context=context)
        obj.create(cr, uid, {'name':'辅料采购','project':result,'executor':uid,'state':'draft','need_endtime':None}, context=context)
        obj.create(cr, uid, {'name':'网版制作','project':result,'executor':uid,'state':'draft','need_endtime':None}, context=context)
        obj.create(cr, uid, {'name':'产品打样','project':result,'executor':uid,'state':'draft','need_endtime':None}, context=context)
        obj.create(cr, uid, {'name':'产品包装','project':result,'executor':uid,'state':'draft','need_endtime':None}, context=context)
        obj.create(cr, uid, {'name':'产品拍摄及修图','project':result,'executor':uid,'state':'draft','need_endtime':None}, context=context)
        obj.create(cr, uid, {'name':'吊牌,插卡,标签','project':result,'executor':uid,'state':'draft','need_endtime':None}, context=context)
        obj.create(cr, uid, {'name':'OPP袋,低压袋','project':result,'executor':uid,'state':'draft','need_endtime':None}, context=context)
        obj.create(cr, uid, {'name':'产品外箱','project':result,'executor':uid,'state':'draft','need_endtime':None}, context=context)
        obj.create(cr, uid, {'name':'海报','project':result,'executor':uid,'state':'draft','need_endtime':None}, context=context)
        obj.create(cr, uid, {'name':'其他','project':result,'executor':uid,'state':'draft','need_endtime':None}, context=context)
        
        return result

    _columns = {

        'name': fields.char(u'产品名称', size=128, select=True, required=True,readonly=True,states={'draft':[('readonly',False)]}),
        
        'to':fields.char(u'研发部对接人', size=128, select=True,readonly=True,states={'draft':[('readonly',False)]}),
        
        'charge':fields.char(u'项目负责人', size=128,readonly=True,states={'draft':[('readonly',False)]}),
        
        "date_start":fields.date(u"开始时间",required=True,readonly=True,states={'draft':[('readonly',False)]}),
        
        "date_end":fields.date(u"完成时间",readonly=True,states={'draft':[('readonly',False)]}),
        
        'note': fields.char(u'说明',readonly=True,states={'draft':[('readonly',False)]},size=512),
        
        'img':fields.binary(u"产品图片",readonly=True,states={'draft':[('readonly',False)]}),
        
        'state': fields.selection([('draft', '开启'),('done','结束')], '项目状态',),
        
    }
    
    _defaults = {
    'date_start':fields.date.context_today,
    'state':lambda *a:'draft',
    }
    
    _order = "date_start desc"
    
    _sql_constraints = [
        ('name', 'unique (name)', '产品名称已存在 !'),
    ]
    
    def case_done(self, cr, uid, ids, *args):
	self.write(cr, uid, ids, {'state': 'done','date_end':time.strftime("%Y-%m-%d %H:%M:%S")})
	return True
    
project()


class conf_task(osv.osv):
    
    _name = "conf_task"
    _description = "配置任务名称"

    _columns = {
    
        'name': fields.char('任务',size=128,select=True,),
        
        'priority': fields.selection(AVAILABLE_PRIORITIES, 'Priority', select=True),
        
    }

conf_task()
