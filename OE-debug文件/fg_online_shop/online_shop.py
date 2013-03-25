# -*- encoding: utf-8 -*-

from osv import osv, fields
import time, tools, datetime

class fg_online_shop_company(osv.osv):

    _name = 'fg_online_shop.company'
    _description = u"经销商"

    _columns = {
        'date_created': fields.date('创建日期', readonly=True),
        'partner_id': fields.many2one('res.partner', '上级经销商', required=False),
        'company_name': fields.char('经销商公司名',size=64,select=True),
        'name':fields.char('法定代表人姓名', size=64, select=True, required=True),
        'phone':fields.char('法定代表人手机号',size=64),
        'license':fields.char('营业执照号',size=64),
        'idc_number':fields.char('法定代表人身份证',size=64),
        'address':fields.char('公司地址',size=128),
        'tel':fields.char('责任人电话',size=64),
        'qq':fields.char('QQ',size=128),
        'email':fields.char('Email',size=64),
        'fax': fields.char('Fax', size=64),
        'is_entity': fields.selection([('True','是'),('False','否')],'是否有实体店铺'),
        'manager':fields.char('负责人',size=64),
        'company_scale':fields.char('公司规模',size=64,),
        'shops':fields.one2many('fg_online_shop.shop', 'company_id', '网店'),
        "website":fields.char("官网", size=64),
        'note':fields.text('备注'),
    }

    _defaults = {
        'date_created': fields.date.context_today,
    }
    
    _sql_constraints=[('online_shop_name_unique','unique(name)','法定代表人姓名不能重复!')]
    

class fg_online_shop_shop(osv.osv):
    _name = 'fg_online_shop.shop'
    _description = "网店"
    
    def unlink(self, cr, uid, ids, context=None):
        if not ids :return super(fg_online_shop_shop, self).unlink(cr, uid, ids, context=context)
        cr.execute('SELECT id FROM fg_online_shop_score WHERE name = %s',(ids[0],))
        idnum = cr.fetchone()
        print idnum,
        if idnum:
            cr.execute('DELETE FROM fg_online_shop_score WHERE name = %s',(ids[0],))
            cr.execute('DELETE FROM fg_online_shop_picrecord WHERE idnum = %s',(idnum,))
            cr.execute('DELETE FROM fg_online_shop_addrecord WHERE idnum = %s',(idnum,))
            cr.execute('DELETE FROM fg_online_shop_minusrecord WHERE idnum = %s',(idnum,))
        cr.commit()
        return super(fg_online_shop_shop, self).unlink(cr, uid, ids, context=context)
    
    _columns = {
        'company_id': fields.many2one('fg_online_shop.company','上级经销商',select=True, required=True),
        'name': fields.char("网店名称",size=64,select=True, required=True),
        'taobaoid':fields.char('掌柜',size=64,select=True),
        'manager':fields.char('负责人',size=64, required=False),
        'managerphone':fields.char('负责人联系方式',size=64,),
        'date_started':fields.char('经营年限',size=64),
        'url':fields.char('网店网址',size=128, required=False),
        'phone':fields.char('法人联系电话',size=64, required=False),
        'legal':fields.char('法人',size=64),
        
        'level':fields.char('店铺等级',size=32),
        'platform':fields.selection([('taobao', '淘宝店'), ('tmall', '天猫商城'), ('360buy', '京东商城'),
            ('amazon', '亚马逊'), ('paipai', '拍拍'), ('independent', '独立'), ('etc', '其他')], '平台', required=False),
        'brand':fields.char('经营品牌',size=128, help='包括非富光的请详细写清楚', required=False),
        'sale_amount':fields.char('年销售规模', size=64),
        'note':fields.text('附注'),
        'scores':fields.one2many('fg_online_shop.score', 'name', '信用积分考核'),
        'auth_state':fields.selection([(u'授权到期',u'授权到期'),(u'已授权',u'已授权'), (u'此店已注销',u'此店已注销'),(u'未授权',u'未授权')
                                            ],'授权状态',),
        "auth_num":fields.char("授权书编号",size=64,select=True, required=False),
        "date_auth_to":fields.date("授权截止日期", required=False),
        "date_auth_start":fields.date("授权开始日期", required=False),
    }
    
    _sql_constraints=[('name_unique','unique(name)','网店名称不能重复!')]
    


    
class fg_online_shop_score(osv.osv):
    
    _name = "fg_online_shop.score"
    
    _description = "信用积分考核"
    
    def write(self, cr, user, ids, vals, context=None):
        res = super(fg_online_shop_score, self).write(cr, user, ids, vals, context=context)
        if not ids :return res
        cr.execute('SELECT sum(point) FROM fg_online_shop_addrecord WHERE idnum = %s GROUP BY idnum',(ids[0],))
        addpoint = cr.fetchall()
        if addpoint :
            if not addpoint[0][0]:
                addpoint = 0
            else:addpoint = int(addpoint[0][0])
        else :addpoint = 0
        cr.execute('SELECT sum(point) FROM fg_online_shop_minusrecord WHERE idnum = %s GROUP BY idnum',(ids[0],))
        minuspoint = cr.fetchall()
        if minuspoint :
            if not minuspoint[0][0]:
                minuspoint = 0
            else:minuspoint = int(minuspoint[0][0])
        else :minuspoint = 0
        date = time.strftime("%Y-%m-%d")
        cr.execute('UPDATE fg_online_shop_score set point = %s,date=%s where id = %s',(60+addpoint-minuspoint,date,ids[0]))
        cr.commit()
        #改颜色
        cr.execute('SELECT id,state,point FROM fg_online_shop_score WHERE point < 60 ORDER BY point DESC')
        point = cr.fetchall()
        length = len(point)
        if length >= 3 :
            a = (point[length-1][0],point[length-2][0],point[length-3][0])
            cr.execute('UPDATE fg_online_shop_score SET state=%s WHERE id in %s',('red',a))
            cr.execute('UPDATE fg_online_shop_score SET state=%s WHERE id not in %s',('blue',a))
        elif length == 2:
            b =  (point[length-1][0],point[length-2][0])
            cr.execute('UPDATE fg_online_shop_score SET state=%s WHERE id in %s',('red',b))
            cr.execute('UPDATE fg_online_shop_score SET state=%s WHERE id not in %s',('blue',b))
        elif length == 1 :
            cr.execute('UPDATE fg_online_shop_score SET state=%s WHERE id = %s',('red',(point[length-1][0])))
            cr.execute('UPDATE fg_online_shop_score SET state=%s WHERE id <> %s',('blue',(point[length-1][0])))
        else :return res
        cr.commit()
        return res
    
    def create(self, cr, user, vals, context=None):
        ids = super(fg_online_shop_score, self).create(cr, user, vals, context=context)
        cr.execute('SELECT sum(point) FROM fg_online_shop_addrecord WHERE idnum = %s GROUP BY idnum',(ids,))
        addpoint = cr.fetchall()
        if addpoint :
            if not addpoint[0][0]:
                addpoint = 0
            else:addpoint = int(addpoint[0][0])
        else :addpoint = 0
        cr.execute('SELECT sum(point) FROM fg_online_shop_minusrecord WHERE idnum = %s GROUP BY idnum',(ids,))
        minuspoint = cr.fetchall()
        if minuspoint :
            if not minuspoint[0][0]:
                minuspoint = 0
            else:minuspoint = int(minuspoint[0][0])
        else :minuspoint = 0
        date = time.strftime("%Y-%m-%d")
        cr.execute('UPDATE fg_online_shop_score set point = %s,date=%s where id = %s',(60+addpoint-minuspoint,date,ids))
        cr.commit()
        #改颜色
        cr.execute('SELECT id,state,point FROM fg_online_shop_score WHERE point < 60 ORDER BY point DESC')
        point = cr.fetchall()
        length = len(point)
        if length >= 3 :
            a = (point[length-1][0],point[length-2][0],point[length-3][0])
            cr.execute('UPDATE fg_online_shop_score SET state=%s WHERE id in %s',('red',a))
            cr.execute('UPDATE fg_online_shop_score SET state=%s WHERE id not in %s',('blue',a))
        elif length == 2:
            b =  (point[length-1][0],point[length-2][0])
            cr.execute('UPDATE fg_online_shop_score SET state=%s WHERE id in %s',('red',b))
            cr.execute('UPDATE fg_online_shop_score SET state=%s WHERE id not in %s',('blue',b))
        elif length == 1 :
            cr.execute('UPDATE fg_online_shop_score SET state=%s WHERE id = %s',('red',(point[length-1][0])))
            cr.execute('UPDATE fg_online_shop_score SET state=%s WHERE id <> %s',('blue',(point[length-1][0])))
        else :return ids
        cr.commit()
        return ids
    
    _columns= {
        
        "name":fields.many2one("fg_online_shop.shop", "网店", select=True, required=True),
        
        "user_id":fields.many2one('res.users', '记录人', readonly=True),
        
        "date":fields.date("更新时间", required=True, readonly=True),
        
        "point":fields.integer(string='信用积分', readonly=True,help="信用积分初始值为60,年度清零."),
        
        "point-add":fields.one2many('fg_online_shop_addrecord', "idnum", '加分记录', ),
        
        "point-minus":fields.one2many('fg_online_shop_minusrecord', "idnum", '减分记录', ),
        
        'note':fields.text('附注'),
        
        "state":fields.char( string='状态',size=64),
        
    }

    _order = "point desc"
    _sql_constraints=[('name_unique','unique (name)','合作商已存在!')]
    _defaults={
        'user_id': lambda obj, cr, uid, context: uid,
        'date':fields.date.context_today,
        'point':60,
        "state" : 'blue'
    }


#记录
class fg_online_shop_addrecord(osv.osv):
    
    _name = "fg_online_shop_addrecord"
    
    _description = "Point Add Record"
    
    def addpic(self, cr, uid, ids, context=None):
        return True
    
    def write(self, cr, user, ids, vals, context=None):
        res = super(fg_online_shop_addrecord, self).write(cr, user, ids, vals, context=context)
        return res
    
    def create(self, cr, user, vals, context=None):
        res = super(fg_online_shop_addrecord, self).create(cr, user, vals, context=context)
        return res
    
    _columns= {
        
        "idnum": fields.many2one("fg_online_shop.score", '加分记录', required=True),
        
        'name' : fields.many2one("fg_online_shop_pointadd", "加分规则", change_default=True),
        
        "point" :fields.integer("分数",),
        
        "user_id":fields.many2one('res.users', '编辑', readonly=True, store=True),
        
        "date":fields.date("违规时间",),
        
        "cover" : fields.binary("违规页面截图",),
        
        "cover2" : fields.binary("违规页面截图",),
    }
    
    def record_change(self, cr, uid, ids, name, context=None):
        if not name:
            return {'value':{'point':0}}
        point = {"point":0}
        result = {}
        obj = self.pool.get('fg_online_shop_pointadd')
        point = obj.read(cr, uid, name, ['point'])
        return {'value':{'point':point["point"]}}
    
    _defaults={
        'user_id': lambda obj, cr, uid, context: uid,
        'date':fields.date.context_today,
        "point" : 0 ,
    }    

class fg_online_shop_minusrecord(osv.osv):
    
    _name = "fg_online_shop_minusrecord"
    
    _description = "Point Minus Record"
    
    _columns= {
        
        "idnum": fields.many2one("fg_online_shop.score", '减分记录', required=True),
        
        'name' : fields.many2one("fg_online_shop_pointminus", "减分规则", change_default=True),
        
        "point" :fields.integer("分数",),
        
        "user_id":fields.many2one('res.users', '编辑', readonly=True),
        
        "date":fields.date("违规时间",),
        
        "cover" : fields.binary("违规页面截图",),
        
        "cover2" : fields.binary("违规页面截图",),
        
    }
    
    def record_change(self, cr, uid, ids, name, context=None):
        if not name:
            return {'value':{'point':0}}
        print ids,context,;
        point = {"point":0}
        result = {}
        obj = self.pool.get('fg_online_shop_pointminus')
        point = obj.read(cr, uid, name, ['point'])
        return {'value':{'point':point["point"]}}
    
    _defaults={
        'user_id': lambda obj, cr, uid, context: uid,
        'date':fields.date.context_today,
        "point" : 0 ,
    } 

#规则
class fg_online_shop_pointadd(osv.osv):
    
    _name = "fg_online_shop_pointadd"
    
    _description = "Point Add Rule"
    
    _columns= {
        
        "name": fields.char("加分规则", size=512, select=True,),
        
        "point" :fields.integer("分数"),
        
        "user_id":fields.many2one('res.users', '编辑', readonly=True),
        
        "date":fields.date("编辑时间", readonly=True),
        
    }
    
    _defaults={
        'user_id': lambda obj, cr, uid, context: uid,
        'date':fields.date.context_today,
    }    

class fg_online_shop_pointminus(osv.osv):
    
    _name = "fg_online_shop_pointminus"
    
    _description = "Point Minus Rule"
    
    _columns= {
        
        "name": fields.char("减分规则", size=512, select=True,),
        
        "point" :fields.integer("分数", ),
        
        "user_id":fields.many2one('res.users', '编辑', readonly=True),
        
        "date":fields.date("编辑时间", readonly=True),
        
    }
    
    _defaults={
        'user_id': lambda obj, cr, uid, context: uid,
        'date':fields.date.context_today,
    }    




class certificate(osv.osv):
    _name = "fg_online_shop.certificate"
    _description = "授权"
    
    
    _columns= {
        "name": fields.char('授权号', size=64, select=True),
        "shop_id":fields.many2one("fg_online_shop.shop", "网店", select=True, change_default=True, required=True),
        "user_id":fields.many2one('res.users', '记录人', readonly=True),
        "date":fields.date("记录时间", required=True),
        'note':fields.text('附注'),
    }
    
    _defaults={
        'user_id': lambda obj, cr, uid, context: uid,
        'date':fields.date.context_today,
    }
    
    

