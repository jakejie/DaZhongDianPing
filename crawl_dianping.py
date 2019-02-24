# -*- coding:utf-8 -*-
__author__ = "jake"
__email__ = "jakejie@163.com"
"""
Project:美团大众点评数据
FileName = PyCharm
Version:1.0
CreateDay:2018/5/17 14:51
"""
from scrapy import cmdline

if __name__ == "__main__":
    cmdline.execute("scrapy crawl dianping".split())
    # cmdline.execute("scrapy crawl dianping --nolog".split())
    pass
