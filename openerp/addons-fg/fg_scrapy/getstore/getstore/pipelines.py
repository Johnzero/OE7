# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

from scrapy.exceptions import DropItem
import sys
import json
import re
import datetime
import os
cdate = datetime.date.today().strftime("%Y-%m-%d")
class GetstorePipeline(object):
    
    def __init__(self):
        
        self.file = open('importstore.json', 'wb')
    
    def process_item(self, item, spider):
        
        reload(sys)
        sys.setdefaultencoding('utf8')
        dirv = os.path.abspath("")
        #taobao
        if 'list-count' in item['title']:
            
            reg2 = 'class="buy-count".*?<span>(.*)</span>'
            sale = re.findall(reg2,item['title'])
            if sale:
                sale = sale[0].replace('<b>','')
                sale =sale.replace('</b>','')
                sale = sale.replace(' ','')
            else:sale = ''
            
            reg3 = '<h4><a href="(.*?)"'
            href = re.findall(reg3,item['title'])
            
            reg6 = 'class="list-place".*?<span>(.*)</span>'
            place = re.findall(reg6,item['title'])
            if not place:place = ['']
            
            reg19 = 'seller-rank-(.*?)"'
            rank = re.findall(reg19,item['title'])
            if not rank:rank = '-1'
            else :rank= rank[0]
            
            reg7 = '<h4>.*?target="_blank".*?>(.*?)</a>'
            name = re.findall(reg7,item['title'])
            name = name[0].replace('<span class="H">','')
            name = name.replace('</span>','')
            name = name.strip()
            
            reg8 = '<a target="_blank" href=.*?>(.*?)</a>'
            owner = re.findall(reg8,item['title'])
            
            if 'mall-icon' in item['title']:
                itemStoreName = u'\u5929\u732b'
            else :itemStoreName = u'\u6dd8\u5b9d\u7f51'
            price = ['']
            title = ''
            
        #else  
        else:
            
            reg = 'class="label-m-info".*?>(.*)</a>'
            ie = re.findall(reg,item['link'])
            if not ie:itemStoreName = ''
            reg4 = '\S+\s+(\S+)'
            itemStoreName = re.findall(reg4,ie[0])
            if not itemStoreName:
                itemStoreName = re.findall(reg,item['link'])
                name = itemStoreName[0].replace(' ','')
            else:name = itemStoreName[0].strip()
            reg5 = '(\S+)\s+'
            itemStoreName = re.findall(reg5,ie[0])
            itemStoreName = itemStoreName[0]
            owner = ['']
            place = ['']
            reg9 = "itemHref':'(.*?)',"
            href = re.findall(reg9,item['title'])
            sale = ''
            reg10 = "itemPrice':'(.*?)',"
            price = re.findall(reg10,item['title'])
            reg11 = 'title="(.*?)"'
            title = re.findall(reg11,item['title'])
            title = title[0].replace('</span>','')
            title = title.replace('"','')
            title = title.replace(' ','')
            rank = '-1'
           
           
        self.file.write("'href':" +'"' + href[0] + '"'+ ','+
                        '"place":' + '"' +place[0] +'"' +',' +
                        '"owner":' + '"' +owner[0] +'"' +',' +
                        '"name":' + '"' +name +'"' +',' +
                        '"itemStoreName":' + '"' +itemStoreName +'"' +','
                        '"date":' + '"' +cdate +'"' +',' +
                        '"title":' + '"' +title +'"' +',' +
                        '"price":' + '"' +price[0] +'"' +',' +
                        '"sale":' + '"' +sale +'"' +',' +
                        '"rank":'+'"'+rank+'"'+','+'\n')
            
        return item
