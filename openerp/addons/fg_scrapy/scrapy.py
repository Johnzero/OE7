# -*- encoding: utf-8 -*-

from osv import osv
from osv import fields
import time
from time import strptime, strftime,time
import datetime
import os
import re
import xlrd,xlwt
import urllib,urllib2
import base64
from bs4 import BeautifulSoup


reslistimg = {}

class scrapy(osv.osv):
    
    _name = "scrapy"
    
    _description = "Scrapy Schedule Everyday"
    
    
    def _get_image(self, cr, uid, ids, name, arg, context=None):
        
        res={}
        
        global reslistimg

        img = self.read(cr,uid,ids,["itemImg"])
        
        if img[0]["itemImg"]:
            
            if img[0]["itemImg"] in reslistimg.keys():
                
                idnum = reslistimg[img[0]["itemImg"]]
                print ids,idnum,type(self.read(cr,uid,idnum,["image"])[0])
				
                res[int(ids[0])] = self.read(cr,uid,idnum,["image"])[0]["image"]
                
            else:
            
                urllib2.socket.setdefaulttimeout(5)
                
                try:
                    req = urllib2.Request(img[0]["itemImg"])
                    response = urllib2.urlopen(req) 
                except:
                    return res
                try:
                    value = response.read()
                except:
                    return res
                
                reslistimg[img[0]["itemImg"]] = [ids[0]]
            
                res[int(ids[0])]= base64.encodestring(value)
        
        return res
    
    _columns = {
        
        'itemHref':fields.char('商品地址', size=512,),
        
        'itemTitle':fields.char('商铺产品名称', size=128,),
        
        'itemImg':fields.char('图片地址',size=512,),
        
        'itemPrice':fields.char('商品价格',size=64),
        
        'itemStoreImg':fields.char('商城图片',size=256,),
        
        'itemStoreName':fields.char('平台',size=128,),
        
        'itemStoreHref':fields.char('店铺地址',size=512),
        
        'href':fields.char('一淘返利',size=512,),
        
        'date':fields.date('抓取时间',),
        
        'item':fields.char('货号',size=64,),
        
        'standardprice':fields.char('标准价格',size=64,),
        
        'name':fields.char('店铺ID',size=64,),
        
    }
    
    _order = "date desc"
    
    def run_scheduler(self, cr, uid, ids=None, context=None):
        
        """通过配置里的商品更新xls，读取xls找到要爬取的商品更新start_urls执行scrapy存储到json文件,通过json文件处理数据读取图片(_get_image)写入数据库
        """
        
        #D:\erp\openerp\addons\scrapyscheduled
        absdir = os.path.abspath('.')
        print absdir
        if not '\\fg_scrapy' in absdir:
                absdir = os.path.abspath('.') + "\\openerp\\addons\\fg_scrapy"
        elif '\\getstore' in absdir:
                absdir = absdir.replace('\\getstore','')
        elif '\\tutorial' in absdir:
                absdir = absdir.replace('\\tutorial','')
        xls = absdir + "\\tutorial\\updateitems.xls"
        orfile =  absdir + "\\tutorial\\items.json"     
        filedir = absdir + "\\tutorial\\datatable.json"
        print absdir,"!!!!"
        absdir = absdir +'\\tutorial'
        #删除旧文件
        try :
            os.remove(filedir)
            os.remove(orfile)
        except :
            pass
        
        #更新updateitems.xls
        obj = self.pool.get("scrapy.item")
        scrapyobj = self.pool.get("scrapy")
        cr.execute('SELECT name,standardprice FROM scrapy_item')
        listitem = cr.fetchall()
        if listitem:
            wb = xlwt.Workbook()
            sheet = wb.add_sheet('sheet 1',)
            sheet.write(0,0,'Item')
            sheet.write(0,1,'Price')
            for row in range(len(listitem)):
                sheet.write(row+1,0,listitem[row][0].upper())
                sheet.write(row+1,1,listitem[row][1])
            wb.save(xls)
        try:
            os.chdir(absdir)
        except:
            return True
        
        print absdir,"**********"
        print filedir
        print xls
        print orfile
        
        cmd = 'scrapy crawl dmoz -o items.json -t json'
        try:
            os.system(cmd)
        except:
           return True

        #读数据
        try:
            datatable = open(filedir,'rb')
        except:
            return True

        #筛选导入数据库
        for items in datatable.readlines():
            if len(items):
                items =eval("{" + items + "}")
                if float(items['itemPrice'])/float(items['standardprice']) < 0.9:
                    items["itemPrice"] = float(items["itemPrice"])
                    items['itemHref']=items['itemHref'].replace('amp;','')
                    items['itemImg'] = items['itemImg'].replace('.jpg_sum','')
                    items['itemImg'] = items['itemImg'].replace('_sum','')
                    items['itemStoreHref'] = items["itemStoreHref"].replace("amp;",'')
                    items['href'] = items['href'].replace('amp;','')
                    scrapyobj.create(cr,uid,items)
        datatable.close()
        print "Done!"
        
        return True

class scrapy_item(osv.osv):
    
    _name = "scrapy.item"
    
    #_inherit = "fuguang.picking.item"
    
    _description = "Product"
    
    _columns ={
        
        'name':fields.char('货号', size=40,),

        'category':fields.selection([(u'FGA事业部',u'FGA事业部'),(u'塑胶事业部',u'塑胶事业部'), (u'安全帽事业部',u'安全帽事业部'), 
                                    (u'玻璃事业部',u'玻璃事业部'), (u'真空事业部',u'真空事业部'),(u'塑胶制品',u'塑胶制品'), (u'财务部',u'财务部'),
                                    (u'其他',u'其他')],'相关事业部',),
        
        'barcode':fields.char('条码', size=20),
        
        'standardprice':fields.float('标准价格',),
        
        'sequence': fields.float('序号', digits=(8, 1)),
        
        'state': fields.selection([('presale', '预售'), ('sale', '在售'), ('expiring', '即将停产'), ('expired', '已停产')], '状态'),
        
        'volume':fields.char('体积', size=40),
        
    }
    
    _order = "name asc"
     
    _sql_constraints = [
        ('item_name_unique', 'unique(name)', '货号不能重复...'),
    ]
    
class scrapy_stores(osv.osv):
    
    _name = "scrapy.stores"
    
    _description = "All Taobao Stores"
    
    _order = "date desc"
    
    _columns={
        
        'name':fields.char('网店',size=64,select=True),
        
        'href':fields.char('网店地址',size=512,),
        
        'itemname':fields.char('品名',size=128,),
        
        'title':fields.char('商品标题',size=128,select=True),
        
        'itemHref':fields.char('商品地址',size=512,),
        
        'place':fields.char('店铺所在地',size=128,),
        
        'owner':fields.char('掌柜ID',size=128,select=True),
        
        'sale':fields.char('销售情况',size=128,),
        
        'date':fields.char('更新时间',size=64),
        
        'itemStoreName':fields.char('平台',size=128,select=True),
        
        'price':fields.char('商品价格',size=128),
        
        'items':fields.one2many('scrapy.store.item', 'store_id', '店铺产品'),
        
	'rank': fields.integer('淘宝等级',select = True),
    }

    _order = "rank desc"
    
    def button(self, cr, uid, ids=None, context=None):
        begintime = time()
        absdir = os.path.abspath('.')
        if not '\\fg_scrapy' in absdir:
                absdir = os.path.abspath('.') + "\\openerp\\addons\\fg_scrapy"
        elif '\\getstore' in absdir:
                absdir = absdir.replace('\\getstore','')
        elif '\\tutorial' in absdir:
                absdir = absdir.replace('\\tutorial','')
            
        orfile =  absdir + "\\getstore\\importstore.json"
        adress =   absdir +'\\getstore'
        fi = absdir +'\\getstore\\'+"stores.json"
        
        try:
            os.chdir(adress)
        except:
            return True
        
        cmd = 'scrapy crawl item -o stores.json -t json'
        
        try:
            os.system(cmd)
        except:
           return True
        
        datatable = open(orfile,'rb')
        
        cr.execute('TRUNCATE scrapy_store_item')
        cr.execute('TRUNCATE scrapy_stores CASCADE')
        cr.commit()
        
        listvalue = {}
        obj = self.pool.get('scrapy.store.item')
        
        for items in datatable.readlines():
            if len(items):
                items =eval("{" + items + "}")
		print items['name'],'*********'
                if not items['itemStoreName'] in ('天猫','淘宝网'):
                    if not (items['itemStoreName'],items["name"]) in listvalue.keys():
			items['rank'] = int(items['rank'])
                        ids = self.create(cr,uid,items)
                        items['store_id'] = ids
                        items['itemHref'] = items['href']
                        #get货号
                        try:
                            requestitem = urllib2.Request(items["itemHref"],headers={"User-Agent":"Mozilla-Firefox5.0"})
                            resitem = urllib2.urlopen(requestitem)
                        except:
                            continue
                        itemdetail = resitem.read()
                        reg2 = '\xbb\xf5\xba\xc5.*?&nbsp;(.*?)</li>'
                        getid = re.findall(reg2,itemdetail)
                        if not getid:
                            reg2 = '\xd0\xcd\xba\xc5.*?&nbsp;(.*?)</li>'
                            getid = re.findall(reg2,itemdetail)
                        if getid:
                            handle = re.findall('[\x80-\xff]',getid[0])
                            m = ''.join(handle)
                            getid = getid[0].replace(m,'').upper()
                        #getid from title
                        if not getid:
                            reg12 = '\w*-\w*'
                            getid = re.findall(reg12,items['title'])
                            if getid:getid = getid[0]
                            else:getid = '富光'


                        items['num'] = getid
                        obj.create(cr,uid,items)
                        listvalue[(items['itemStoreName'],items["name"])] = ids
                    else:
                        idnum = listvalue[(items['itemStoreName'],items["name"])]
                        items['store_id'] = idnum
                        items['itemHref'] = items['href']
                        #get货号
                        try:
                            requestitem = urllib2.Request(items["itemHref"],headers={"User-Agent":"Mozilla-Firefox5.0"})
                            resitem = urllib2.urlopen(requestitem)
                        except:
                            continue
                        itemdetail = resitem.read()
                        reg2 = '\xbb\xf5\xba\xc5.*?&nbsp;(.*?)</li>'
                        getid = re.findall(reg2,itemdetail)
                        if not getid:
                            reg2 = '\xd0\xcd\xba\xc5.*?&nbsp;(.*?)</li>'
                            getid = re.findall(reg2,itemdetail)
                        if getid:
                            handle = re.findall('[\x80-\xff]',getid[0])
                            m = ''.join(handle)
                            getid = getid[0].replace(m,'').upper()
                        if not getid:
                            reg12 = '\w*-\w*'
                            getid = re.findall(reg12,items['title'])
                            if getid:getid = getid[0]
                            else:getid = '富光'
                        items['num'] = getid
                        
                        obj.create(cr,uid,items)
                #淘宝
                else:
                    #http://shop33320566.taobao.com/?order=&queryType=all&browseType=grid&searchWord=%B8%BB%B9%E2&price1=&price2=
                    #http://shop33320566.taobao.com/?spm=0.0.0.131.QifcLQ&pageNum=2&catId=null&categoryName=null&encodeCategoriesName=y&price1=&price2=&searchWord=%B8%BB%B9%E2&order=null&queryType=all&browseType=grid
                    #http://shop33320566.taobao.com/?&pageNum=2&searchWord=%B8%BB%B9%E2&queryType=all&browseType=grid
                    url = items["href"] + '//search.htm?&search=y&keyword=%B8%BB%B9%E2&searchWord=%B8%BB%B9%E2&pageNum=1'
                                            #/?order=&searchWord=%B8%BB%B9%E2
                    try:
                        request = urllib2.Request(url,headers={"User-Agent":"Mozilla-Firefox5.0"})
                        res = urllib2.urlopen(request)
                    except:
                        continue
                    data = res.read()
                    reg = 'class="page-info">.*?/(.*?)<'
                    num = re.findall(reg,data)
                    print num
                    print url,'-----'
                    if num:
                        if num[0] == '0':continue
                        #cr.execute('delete from scrapy_stores \
                        #           where id=%s', (int(ids),))
                        #cr.commit()
                    else:continue
                    if not num[0]:continue
		    items['rank'] = int(items['rank'])
                    ids = self.create(cr,uid,items)
                    oritem = items["href"]
                    for n in range(1):
                        itempage = oritem + '//search.htm?&search=y&keyword=%B8%BB%B9%E2&searchWord=%B8%BB%B9%E2&pageNum=' + str(1)
                        try:
                            requestpage = urllib2.Request(itempage,headers={"User-Agent":"Mozilla-Firefox5.0"})
                            respage = urllib2.urlopen(requestpage)
                        except:
                            continue
                        datapage = respage.read()
                        shoplist = ''
                        soup = BeautifulSoup(datapage,from_encoding="gb18030")
                        shoplist = soup.findAll('div',{'class':'grid'})
                        shoplistitem = ''
                        for each in shoplist:
                            if 'keyword' in str(each):
                                shoplistitem = each
                        #模板不同
                        if shoplistitem:
                            
                            soupdata = shoplistitem.findAll('div',{'class':'item'})
                            for eachsoup in range(len(soupdata)):
                                subdivpic =  soupdata[eachsoup].find('div',{'class':'pic'})
                                subdivdesc =  soupdata[eachsoup].find('div',{'class':'desc'})
                                subdivsales =  soupdata[eachsoup].find('div',{'class':'sales-amount'})
                                subdivrating =  soupdata[eachsoup].find('div',{'class':'rating'})
                                subdivprice = soupdata[eachsoup].find('div',{'class':'price'})
                                items["itemHref"] = subdivpic.a.get("href") or ''
                                if 'src2' in str(subdivpic):
                                    items["itemImg"] = subdivpic.img["src2"]
                                elif 'src' in str(subdivpic):
                                    items["itemImg"] = subdivpic.img["src"]
                                else:items["itemImg"]=''
                                items["title"] = ''.join(x for x in subdivdesc.text or '')
                                items["price"] = ''.join(x for x in subdivprice.strong.text or '')
                                if subdivsales:
                                    items["sale"] = ''.join(x for x in subdivsales.text)
                                else:items["sale"]=''
                                items['store_id'] = ids
                                try:
                                    resitem = urllib2.urlopen(items["itemHref"])
                                except :
                                    continue
                                itemdetail = resitem.read()
                                reg2 = '\xbb\xf5\xba\xc5.*?&nbsp;(.*?)</li>'
                                getid = re.findall(reg2,itemdetail)
                                if not getid:
                                    reg2 = '\xd0\xcd\xba\xc5.*?&nbsp;(.*?)</li>'
                                    getid = re.findall(reg2,itemdetail)
                                if getid:
                                    handle = re.findall('[\x80-\xff]',getid[0])
                                    m = ''.join(handle)
                                    getid = getid[0].replace(m,'').upper()
                                    getid = getid.replace('ML','')
                                if not getid:getid = '富光'
                                items['num'] = getid
                                obj.create(cr,uid,items)
                        else:
                            shoplist = soup.findAll('div',{'class':'item3line1'})
                            if not shoplist:shoplist = soup.findAll('div',{'class':'item4line1'})
                            for eachsoup in shoplist:
                                subitem = eachsoup.findAll('dl',{'class':'item'})
                                for it in subitem:
                                    subdivpic = it.find('dt',{'class':'photo'})
                                    items["itemHref"] = subdivpic.a.get("href") or ''
                                    if 'src2' in str(subdivpic):
                                        items["itemImg"] = subdivpic.img["src2"]
                                    elif 'src' in str(subdivpic):
                                        items["itemImg"] = subdivpic.img["src"]
                                    else:items["itemImg"]=''
                                    subdivdesc = it.find('dd',{'class':'detail'})
                                    items["title"] = ''.join(x for x in subdivdesc.a.text)
                                    items["price"] = subdivdesc.div.div.find('span',{'class':'c-price'}).text
                                    items["price"] = ''.join(x for x in items["price"])
                                    items['store_id'] = ids
                                    try:
                                        requestitem = urllib2.Request(items["itemHref"],headers={"User-Agent":"Mozilla-Firefox5.0"})
                                        resitem = urllib2.urlopen(requestitem)
                                    except:
                                        continue
                                    itemdetail = resitem.read()
                                    reg2 = '\xbb\xf5\xba\xc5.*?&nbsp;(.*?)</li>'
                                    getid = re.findall(reg2,itemdetail)
                                    if not getid:
                                        reg2 = '\xd0\xcd\xba\xc5.*?&nbsp;(.*?)</li>'
                                        getid = re.findall(reg2,itemdetail)
                                    if getid:
                                        handle = re.findall('[\x80-\xff]',getid[0])
                                        m = ''.join(handle)
                                        getid = getid[0].replace(m,'').upper()
                                    if not getid:getid = '富光'
                                    items['num'] = getid
                                    obj.create(cr,uid,items)
                                
                    
        if os.path.isfile(fi):os.remove(fi)
        
        #create store_items
        #alldata = cr.execute('SELECT id,href,')
        endtime = time()
        print 'Done!',str((endtime-begintime)/60)+'min'
        
        return True
    
class scrapy_store_item(osv.osv):
    
    _name = "scrapy.store.item"
    
    _description = "All Store Items"
    
    _order = "date desc"
    
    _columns={
        
        'store_id':fields.many2one('scrapy.stores','网店',select=True, required=True),
        
        'title':fields.char('商品标题',size=128,select=True),
        
        'num':fields.char('货号',size=128),
        
        'price':fields.char('商品价格',size=128),
        
        'itemHref':fields.char('商品地址',size=512,),
        
        'sale':fields.char('销售情况',size=128,),
        
        'date':fields.char('更新时间',size=64),
        
        'owner':fields.char('掌柜',size=128,),
        
        'itemStoreName':fields.char('平台',size=128,),
        
        'itemImg':fields.char('图片地址',size=512,),
        
    }
