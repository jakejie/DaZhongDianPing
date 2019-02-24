# -*- coding: utf-8 -*-
BOT_NAME = 'DaZhongDianPing'
SPIDER_MODULES = ['DaZhongDianPing.spiders']
NEWSPIDER_MODULE = 'DaZhongDianPing.spiders'

# 数据库连接信息
db_host = '****'
db_user = 'root'
db_pawd = '***'
db_name = 'dp'
db_port = 3306

# 代理ip配置
use_proxy = True
'''阿布云代理'''
abu_proxy_server = "http://http-dyn.abuyun.com:9020"
abu_proxy_user = "*****"
abu_proxy_pass = "****"
'''讯代理'''
x_proxy_server = "http://forward.xdaili.cn:80"
x_proxy_secret = "****"
x_proxy_orderno = "****"

# COOKIES_ENABLED = False
# REDIRECT_ENABLED = False
# ROBOTSTXT_OBEY = False
# RETRY_ENABLED = False
# RETRY_TIMES = 5
# RETRY_HTTP_CODECS = [500, 502, 503, 504, 408, 403, 400, 429, 302]
# # HTTPERROR_ALLOWED_CODES = [400, 429, 500, 403]  # 上面报的是403，就把403加入
# CONCURRENT_REQUESTS = 500
# # DOWNLOAD_DELAY = 3
# CONCURRENT_REQUESTS_PER_DOMAIN = 500
# CONCURRENT_REQUESTS_PER_IP = 500
# DOWNLOAD_TIMEOUT = 60
# DOWNLOADER_MIDDLEWARES = {
#     'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
#     'DaZhongDianPing.middlewares.ProxyMiddleware': 110,
#     'scrapy.downloadermiddlewares.retry.RetryMiddleware': 120,
#     'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 130,
# }
#
# ITEM_PIPELINES = {
#     'DaZhongDianPing.pipelines.DazhongdianpingPipeline': 300,
# }
