# -*- coding:utf-8 -*-
__author__ = "jake"
__email__ = "jakejie@163.com"
"""
Project:DaZhongDianPing
FileName = PyCharm
Version:1.0
CreateDay:2018/7/4 14:44
"""
from scrapy import cmdline

if __name__ == "__main__":
    cmdline.execute("scrapy crawl business_update".split())
    pass
