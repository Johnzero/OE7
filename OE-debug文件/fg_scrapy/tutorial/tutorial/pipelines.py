# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
# coding: utf-8
from scrapy.exceptions import DropItem
import sys
import json
import re
import datetime
import os
import xlrd

cdate = datetime.date.today().strftime("%Y-%m-%d")
class JsonWriterPipeline(object):
    
    def __init__(self):
        self.file = open('datatable.json', 'wb')
    
    def process_item(self, item, spider):
        
        reload(sys)
        sys.setdefaultencoding('utf8')
        dirv = os.path.abspath("")
        wkb = xlrd.open_workbook(dirv+"\\"+"updateitems.xls")
        sheet = wkb.sheets()[0]
        
        reg = '<a(.*?)</a>'
        listitem = re.findall(reg,item["title"])
        if listitem:
            li = listitem[0]
               
            reg2 = ('\"(\'itemHref.*?)\"')
            li2 = re.findall(reg2,li)
            reg3 = ('href=\\"(.*?)"')
            li3 = re.findall(reg3,li)
        else:
            li = ''
            li2 = ['']
            li3 = ['']
            
        reg4 = (';q=(.*?)&amp;')
        li4 = re.findall(reg4,li)
        price = 0
        if li4:
            for rows in range(sheet.nrows):
                if li4[0].strip() == sheet.cell(rows,0).value.strip():
                    price = sheet.cell(rows,1).value
        else:price = 0
        #get storename
        reg2 ='>(.*)</a>'
        name = re.findall(reg2,item['link'])
        reg = '[u"\xa0"]+(.*)'
        name = re.findall(reg,name[0])
        if not len(name):
            name = [""]
        self.file.write(li2[0] + ''','href':''' + "'" + li3[0] + "'" + ",'date':" + "'" + cdate + "'" + ",'item':" + "'" +
                        li4[0] + "'"  + ",'standardprice':" + "'" + str(price) + "'" + ",'name':" + "'" + str(name[0].strip()) + "'" + '\n' )
        
        return item



