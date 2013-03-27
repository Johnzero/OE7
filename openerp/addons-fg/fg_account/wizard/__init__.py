# -*- coding: utf-8 -*-

from osv import osv, fields
import time, xlrd, base64
from tools import DEFAULT_SERVER_DATE_FORMAT
import xlwt, cStringIO

class cash_bill_import(osv.osv_memory):
    _name = "fg_account.cash_bill.import.wizard"
    _description = "导入现金账单明细"
    
    _columns = {
        'excel': fields.binary('excel文件', filters='*.xls'),
    }
    
    
    def import_bill(self, cr, uid, ids, context=None):
        result = {'type': 'ir.actions.act_window_close'}
        for wiz in self.browse(cr,uid,ids):
            if not wiz.excel: continue
            excel = xlrd.open_workbook(file_contents=base64.decodestring(wiz.excel))
            sh = excel.sheet_by_index(0)
            
            bill_obj = self.pool.get('fg_account.bill')
            act_obj = self.pool.get('ir.actions.act_window')
            mod_obj = self.pool.get('ir.model.data')
            partner_obj = self.pool.get('res.partner')
            
            new_ids = []
            for rx in range(sh.nrows):
                #如果第一个单元格是日期，则解析.
                date_s = sh.cell(rx, 0).value
                cash_in = sh.cell(rx, 3).value

                if not cash_in: continue
                
                try:
                    date = time.strptime(date_s.strip(),'%Y.%m.%d')
                except:
                    continue
                
                data = {
                    'user_id':uid,
                    'date_paying':time.strftime(DEFAULT_SERVER_DATE_FORMAT, date),
                    'category_id':1,
                    'note':sh.cell(rx, 1).value,
                    'amount':float(cash_in),
                }
                #check for partner_id
                partner_name = str(sh.cell(rx, 2).value).strip()
                if partner_name:
                    partner_list = partner_obj.search(cr, uid, [('name','=',partner_name)])
                    if partner_list:
                        data['partner_id'] = partner_list[0]

                id = bill_obj.create(cr, uid, data)
                new_ids.append(id)
            
            result = mod_obj.get_object_reference(cr, uid, 'fg_account', 'action_fg_account_bill_all')
            id = result and result[1] or False
            result = act_obj.read(cr, uid, [id], context=context)[0]
            result['domain'] = "[('id','in', ["+','.join(map(str, new_ids))+"])]"
            
        return result
            
            
class bank_bill_import(osv.osv_memory):
    _name = "fg_account.bank_bill.import.wizard"
    _description = "导入银行账单明细"
    
    _columns = {
        'excel': fields.binary('excel文件', filters='*.xls'),
    }
    
    def import_bill(self, cr, uid, ids, context=None):
        result = {'type': 'ir.actions.act_window_close'}
        for wiz in self.browse(cr,uid,ids):
            if not wiz.excel: continue
            
            excel = xlrd.open_workbook(file_contents=base64.decodestring(wiz.excel))
            sh = excel.sheet_by_index(0)
            
            bill_obj = self.pool.get('fg_account.bill')
            act_obj = self.pool.get('ir.actions.act_window')
            mod_obj = self.pool.get('ir.model.data')
            partner_obj = self.pool.get('res.partner')

            new_ids = []
            for rx in range(sh.nrows):
                #如果第一个单元格是日期，则解析.
                date_s = sh.cell(rx, 0).value
                cash_in = sh.cell(rx, 3).value

                if not cash_in: continue
                
                try:
                    date = time.strptime(date_s.strip(),'%Y.%m.%d')
                except:
                    continue
                
                data = {
                    'user_id':uid,
                    'date_paying':time.strftime(DEFAULT_SERVER_DATE_FORMAT, date),
                    'note':sh.cell(rx, 1).value,
                    'category_id':2,
                    'amount':float(cash_in),
                }
                #check for partner_id
                partner_name = sh.cell(rx, 2).value.strip()
                if partner_name:
                    partner_list = partner_obj.search(cr, uid, [('name','=',partner_name)])
                    if partner_list:
                        data['partner_id'] = partner_list[0]

                id = bill_obj.create(cr, uid, data)
                new_ids.append(id)
            
            result = mod_obj.get_object_reference(cr, uid, 'fg_account', 'action_fg_account_bill_all')
            id = result and result[1] or False
            result = act_obj.read(cr, uid, [id], context=context)[0]
            result['domain'] = "[('id','in', ["+','.join(map(str, new_ids))+"])]"
            
        return result

class confirm_customer(osv.osv_memory):
    _name = "fg_account.bank_bill.customer.confirm.wizard"
    _description = "确认客户"
    
    _columns = {
        'partner_id': fields.many2one('res.partner', '客户', required=True),
    }
    
    def view_init(self, cr, uid, fields_list, context=None):
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False)
        bill = self.pool.get('fg_account.bill').browse(cr, uid, record_id, context=context)
        if bill.state != 'draft':
            raise osv.except_osv('提醒','所选单据中有些已经确认过客户.')
        return False
    
    def confirm_customer(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        bill_obj = self.pool.get('fg_account.bill')
        
        data = self.read(cr, uid, ids, [], context=context)[0]
        
        record_id = context and context.get('active_ids', False)

        bill_obj.write(cr, uid, record_id, { 
            'partner_id': data['partner_id'][0], 
            }
        )
        
        return {'type': 'ir.actions.act_window_close'}


class reconcile_wizard(osv.osv_memory):
    _name = "fg_account.reconcile.confirm.wizard"
    _description = "对账"
    
    _columns = {
        'confirm':fields.boolean('确认对账/取消对账'),   
    }
    
    def confirm(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        
        period_check_obj = self.pool.get('fg_account.period.check')
        order_obj = self.pool.get('fg_sale.order')
        bill_obj = self.pool.get('fg_account.bill')
        
        data = self.read(cr, uid, ids, [], context=context)[0]
        record_ids = context and context.get('active_ids', False)
        for record in period_check_obj.browse(cr, uid, record_ids, context):
            if record.ref_doc._table_name == 'fg_sale.order':
                order_obj.write(cr, uid, [record.id], {'reconciled':data['confirm']})
                
            if record.ref_doc._table_name == 'fg_account.bill':
                rid = record.id - 1000000000
                bill_obj.write(cr, uid, [rid], {'reconciled':data['confirm']})
        
        return {'type': 'ir.actions.act_window_close'}


class reconcile_view_wizard(osv.osv_memory):
    _name = "fg_account.reconcile.view.wizard"
    _description = "对账单明细"
    
    _columns = {
        'partner_id': fields.many2one('res.partner', '客户', required=True),
        #'reconciled':fields.boolean('已对账'),
        'date_start': fields.date('开始日期', required=True),
        'date_end': fields.date('结束日期', required=True),
    }
    
    _defaults = {
        'date_end': fields.date.context_today,
    }
    
    def view(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids)[0]
        
        #计算之前的汇总
        statement = """
        SELECT
        	pc."t" AS T,
        	SUM(pc.amount)AS total_amount
        FROM
        	fg_account_period_check pc
        WHERE
        	pc.o_partner = %s
        AND pc.o_date < to_date('%s', 'YYYY-MM-DD')
        GROUP BY
        	T
        """
        amount_dict = dict()
        cr.execute(statement % (this.partner_id.id, this.date_start))

        for row in cr.fetchall():
            amount_dict[row[0]] = row[1]
        
        sent = amount_dict.get(u'发货额', 0)
        back = amount_dict.get(u'退回', 0)  #负数
        cash_in = amount_dict.get(u'收现', 0)
        bank_in = amount_dict.get(u'转帐', 0)
        discount = amount_dict.get(u'让利', 0)
        
        #期初余额
        inital_amount = sent + back - cash_in - bank_in - discount

        
        # search and save the result to reconcile_item table.
        period_check_obj = self.pool.get('fg_account.period.check')
        reconcile_item_obj = self.pool.get('fg_account.reconcile.item')
        item_ids = period_check_obj.search(cr, uid, [('o_partner','=',this.partner_id.id),
                ('o_date','>=',this.date_start),('o_date','<=',this.date_end)], order='ID ASC')
        
        last_amount = inital_amount
        ids = []
        for item in period_check_obj.read(cr, uid, item_ids):
            if item['t'] in [u'退回',u'发货额']:
                last_amount = last_amount + item['amount']
            else:
                last_amount = last_amount - item['amount']
            
            id = reconcile_item_obj.create(cr, uid, {
                'ref_doc':item['ref_doc'],
                'o_date':item['o_date'],
                'name':item['name'],
                'o_partner':item['o_partner'][0],
                't':item['t'],
                'reconciled':item['reconciled'],
                'cleared':item['cleared'],
                'amount':item['amount'],
                'balance':last_amount,
                'note':item['note'],
            })
            ids.append(id)
        
        act_obj = self.pool.get('ir.actions.act_window')
        mod_obj = self.pool.get('ir.model.data')

        result = mod_obj.get_object_reference(cr, uid, 'fg_account', 'action_fg_account_reconcile_item_tree_view')

        id = result and result[1] or False

        result = act_obj.read(cr, uid, [id], context=context)[0]
        result['domain'] = "[('id','in', ["+','.join(map(str, ids))+"])]"
        result['limit'] = 1000
        return result
        

class reconcile_export(osv.osv_memory):
    _name = "fg_account.reconcile.export.wizard"
    _description = "对账单导出"
    
    
    _columns = {
        'partner_ids': fields.many2many('res.partner', 'rel_partner_reconcile_export_wizard', 'wiz_id', 'partner_id', '客户',  required=True),
        'reconciled':fields.boolean('已对账'),
        'date_start': fields.date('开始日期',  required=True),
        'date_end': fields.date('结束日期',  required=True),
        'name': fields.char('文件名', 16,),
        'data': fields.binary('文件',),
        'state': fields.selection( [('choose','choose'),   # choose
                                     ('get','get'),         # get the file
                                   ] ),
    }
    
    _defaults = {
        'date_end': fields.date.context_today,
        'state': lambda *a: 'choose',
        'name': 'reconcile.xls',
    }
    
    
    def export_excel(self, cr, uid, ids, context=None):
        book = xlwt.Workbook(encoding='utf-8')
        
        this = self.browse(cr, uid, ids)[0]
        
        for partner in this.partner_ids:
            
            #计算
            statement = """
            SELECT
                    pc."t" AS T,
                    SUM(pc.amount)AS total_amount
            FROM
                    fg_account_period_check pc
            WHERE
                    pc.reconciled = %s
            AND pc.o_partner = %s
            AND pc.o_date < to_date('%s', 'YYYY-MM-DD')
            GROUP BY
                    T
            """
            amount_dict = dict()
            cr.execute(statement % (this.reconciled, partner.id, this.date_start))
            for row in cr.fetchall():
                amount_dict[row[0]] = row[1]
            
            sent = amount_dict.get(u'发货额', 0)
            back = amount_dict.get(u'退回', 0)
            cash_in = amount_dict.get(u'收现', 0)
            bank_in = amount_dict.get(u'转帐', 0)
            discount = amount_dict.get(u'让利', 0)
            inital_amount = sent + back - cash_in - bank_in - discount
            
            sql = """
            SELECT
                o_date,
                    name,
                    t,
                    reconciled,
                    amount,
                    note
            FROM
                    fg_account_period_check
            WHERE
                    reconciled = %s
            AND o_partner = %s
            AND o_date >= to_date('%s', 'YYYY-MM-DD')
            AND o_date <= to_date('%s', 'YYYY-MM-DD')
            ORDER BY o_date asc
            """
            
            
            sheet1 = book.add_sheet(partner.name)
            sheet1.write(0, 0, '客户: %s' % partner.name)
            sheet1.write(0, 1, '开始日期: %s' % this.date_start)
            sheet1.write(0, 2, '截止日期: %s' % this.date_end)
            
            sources = ['日期','单号','发货额','退货','收现','备注','转账','让利','余额','是否对账']
            c_i = 0
            for c in sources:
                sheet1.write(1, c_i, c)
                c_i = c_i + 1
            sheet1.write(0, 7, '期初余额: %s' % inital_amount)
            
            i = 2
            last_amount = inital_amount
            
            cr.execute(sql % (this.reconciled, partner.id, this.date_start, this.date_end))
            for p in cr.fetchall():
                sheet1.write(i, 0, p[0])
                sheet1.write(i, 1, p[1])
                sheet1.write(i, 9, p[3] and '是' or '否')
                sheet1.write(i, 5, p[5])
                
                if p[2] == '发货额':
                    last_amount = last_amount + p[4]
                    sheet1.write(i, 2, p[4])
                elif p[2] == '退货':
                    last_amount = last_amount + p[4]
                    sheet1.write(i, 3, p[4])
                elif p[2] == '现金':
                    last_amount = last_amount + p[4]
                    sheet1.write(i, 4, p[4])
                elif p[2] == '转账':
                    last_amount = last_amount + p[4]
                    sheet1.write(i, 6, p[4])
                elif p[2] == '让利':
                    last_amount = last_amount + p[4]
                    sheet1.write(i, 7, p[4])
                    
                sheet1.write(i, 8, last_amount)
                
                i = i + 1
        
        buf=cStringIO.StringIO()
        book.save(buf)

        out=base64.encodestring(buf.getvalue())

        return self.write(cr, uid, ids, {'state':'get', 'data':out, 'name':this.name }, context=context)
        