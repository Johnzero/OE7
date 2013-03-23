# -*- coding: utf-8 -*-

import urllib2,urllib
import thread
import threading,time
from random import choice
from time import sleep

user_agents = [
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
    'Opera/9.25 (Windows NT 5.1; U; en)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
    'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9'
]

class Login(threading.Thread):
    def __init__(self, thread_id):  
        threading.Thread.__init__(self)  
        self.thread_id = thread_id
        self.thread_stop = False
    def run(self):
	#print 'Thread %s is running,time:%s\n' %(self.getName(),time.ctime())
        while 1:
	    version = choice(user_agents)
	    url = 'http://mark.sina.com.cn/v2/DoData.php?p_mark=nba_ding&question[]=152&&option_152=728&type=get&i_mark=news_12376'
	    headers = { 'User-Agent' : version }
	    values = {'name' : 'Michael Foord','location' : 'Northampton','language' : 'Python' }
	    try:
		data = urllib.urlencode(values)
		req = urllib2.Request(url,data,headers)
		req.add_header("Referer","http://china.nba.com/news/4/2013-03-23/1303/12376.html")
		resp = urllib2.urlopen(req)
		print resp.read()
		resp.close()
	    except :
		req = 0
		sleep(5)

def makethread(n):
    for thread_id in range(n):
        thread = Login(thread_id)
        thread.start()
	
if __name__ == '__main__':
    
    makethread(300)