# Scrapy settings for getstore project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'getstore'

SPIDER_MODULES = ['getstore.spiders']
NEWSPIDER_MODULE = 'getstore.spiders'
ITEM_PIPELINES = ['getstore.pipelines.GetstorePipeline']
# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'getstore (+http://www.yourdomain.com)'
#LOG_FILE = r'C:\Users\Administrator\Desktop\log2.txt'
LOG_LEVEL = 'WARNING'
DOWNLOAD_TIMEOUT = 540
DOWNLOAD_DELAY = 1