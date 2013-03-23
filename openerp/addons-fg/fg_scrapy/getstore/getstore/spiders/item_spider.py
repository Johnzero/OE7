# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from getstore.items import GetstoreItem
from scrapy.shell import inspect_response
import re
import xlrd
import os,sys
import urllib2
#http://s.etao.com/search?q=fgl&sort=price-asc&mt=144&s=0#filterbar

class ItemSpider(BaseSpider):
	
    name = "item"
    allowed_domains = [""]
    reload(sys)
    #socket.setdefaulttimeout(8.0)
    sys.setdefaultencoding('utf8')
    dirf = os.path.abspath('.')
    
    itemname = []
    urls = []
    listurls = []
    
    urls = ['http://shopsearch.taobao.com/search?v=shopsearch&q=%B8%BB%B9%E2','http://s.etao.com/search?spm=1002.8.1.1272.AMP1SB&q=%B8%BB%B9%E2&style=grid&initiative_id=setao_20121101&fseller=%BE%A9%B6%AB%C9%CC%B3%C7%2C%D1%C7%C2%ED%D1%B7%2C%B5%B1%B5%B1%CD%F8%2C%BF%E2%B0%CD%B9%BA%CE%EF%2C2688%CD%F8%B5%EA%2C1%BA%C5%B5%EA%2C%B2%A9%BF%E2%CA%E9%B3%C7%2C%D6%D0%D3%CA%BF%EC%B9%BA%2C%D6%D0%B9%FA%BB%A5%B6%AF%B3%F6%B0%E6%CD%F8%2C%C8%FD%CC%E6%B9%BA%CE%EF%CD%F8%B9%D9%CD%F8%2C%C0%FB%C8%BA%D2%BD%D2%A9%D0%C5%CF%A2%CD%F8%2C99%CD%F8%C9%CF%CA%E9%B3%C7%2C%C0%FB%C8%BA%C9%CC%B3%C7%2C%D2%BB%BA%C5%C9%CC%B3%C7%B9%D9%CD%F8%2C%B5%C0%CE%BB%B9%BA%C9%CC%B3%C7%2C%C2%F2%B2%E8%CD%F8%2C%C2%F2%B6%E0%CD%F8%2C%B9%C5%BC%AE%CD%F8%2CQQ%CD%F8%B9%BA%B9%D9%CD%F8%2C%B5%E3%B5%E3%CD%F8%2C%CE%B5%C0%B6%CA%E9%B5%EA%2C%D6%D0%B9%FA%CD%BC%CA%E9%CD%F8%2C%CD%F8%C9%CF%CC%EC%BA%E7%B9%D9%CD%F8%2C%C8%CA%BA%CD%B4%BA%CC%EC%B0%D9%BB%F5%2C%D2%F8%C1%AA%D4%DA%CF%DF%2C%BC%D2%C0%D6%B8%A3%D4%DA%CF%DF%C9%CC%B3%C7%2C%C2%F3%B5%C2%C1%FA%B9%D9%B7%BD%CD%F8%C9%CF%C9%CC%B3%C7',
	   ]
    
    for url in urls:
	if not 'shopsearch' in url: 
	    try:
		request = urllib2.Request(url,headers={"User-Agent":"Mozilla-Firefox5.0"})
		res = urllib2.urlopen(request)
	    except:
		pass
	    data = res.read()
	    
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
			for n in range(num):
			    urladd = url + "&s=" + str(n*36)
			    if not urladd in listurls:
				listurls.append(urladd)
		    else:
			listurls.append(url)
	    else:
		continue
	
	else:
	    try:
		request = urllib2.Request(url,headers={"User-Agent":"Mozilla-Firefox5.0"})
		res = urllib2.urlopen(request)
	    except:
		pass
	    data = res.read()
	    reg3 = 'class="correction-panel"'
	    noresult = re.findall(reg3,data)
	    if not noresult:
		if data:
		    reg2 = "\xb9\xb2(.*)\xd2\xb3"
		    string = re.findall(reg2,data)
		    if string:
			num = int(string[0])
			urladd = ''
			for n in range(num):
			    urladd = url + "&s=" + str(n*20)
			    if not urladd in listurls:
				listurls.append(urladd)
		    else:
			listurls.append(url)
	    else:
		continue
    #test	    
    for l in range(len(listurls)):
	if l %2==0:del listurls[l]
    start_urls = [ l for l in listurls]
    #start_urls = ['http://shopsearch.taobao.com/search?q=%B8%BB%B9%E2&v=shopsearch&fs=1&jumpto=1&s=0&n=120']	
    
    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        sites = hxs.select('//div[@class="griditem"]')
	items = []
	if sites:
	    for site in sites:
		item = GetstoreItem()          
		item['title'] = site.select('h2[@class="title"]').extract()[0]
		item['link'] = site.select('div/div/a[@class="label-m-info"]').extract()[0]
		items.append(item)
	    
	else:
	    sites = hxs.select('//li[@class="list-item"]')
	    for a in sites:
		it = GetstoreItem()          
		it['title'] = a.extract()
		items.append(it)
        
	return items
