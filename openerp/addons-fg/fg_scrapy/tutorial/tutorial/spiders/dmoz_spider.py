# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
# -*- encoding: utf-8 -*-
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from tutorial.items import DmozItem
from scrapy.shell import inspect_response
import re
import xlrd
import os
import urllib2

#http://s.etao.com/search?q=fgl&sort=price-asc&mt=144&s=0#filterbar

class DmozSpider(BaseSpider):
	
    name = "dmoz"
    allowed_domains = [""]
    dirf = os.path.abspath(".")
    wkb = xlrd.open_workbook(dirf+"\\updateitems.xls")
    sheet = wkb.sheets()[0]
    
    itemname = []
    urls = []
    listurls = []
    
    for rows in range(sheet.nrows):
	if rows >0:
	    itemname.append(sheet.cell(rows,0).value)
    print itemname
    for product in itemname:
	urls.append("http://s.etao.com/search?&q="+product+"&sort=price-asc" +"&style=grid") 
    
    for url in urls:
	print url
	try:
	    request = urllib2.Request(url,headers={"User-Agent":"Mozilla-Firefox5.0"})
	    res = urllib2.urlopen(request)
	except:
	    pass
	data = res.read()
	print len(data)
	
	reg3 = 'class="correction-panel"'
	noresult = re.findall(reg3,data)
	
	if not noresult:
	    if data:
		reg = '<span>(.*)</span><span>'
		reg2 = "\xb9\xb2(.*)\xd2\xb3"
		string = re.findall(reg,data)
		if string:
		    string2= re.findall(reg2,string[0])
		    num = int(string2[0])
		    urladd = ''
		    print num
		    for n in range(num):
			urladd = url + "&s=" + str(n*36)
			if not urladd in listurls:
			    listurls.append(urladd)
		else:
		    listurls.append(url)
	else:
	    continue
	
	print len(listurls),"****"
    
    start_urls = [it for it in listurls]
    #start_urls = ['http://s.etao.com/search?&q=FZ6010-1500&sort=price-asc&style=grid']
    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        sites = hxs.select('//div[@class="griditem"]')
        items = []
        for each in sites:
	    item = DmozItem()          
	    item['title'] = each.select('h2[@class="title"]').extract()[0]
	    item['link'] = each.select('div[@class="oper clear-fix shoptext"]').extract()[0]
	    items.append(item)
        return items
    
    
