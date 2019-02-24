# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


# 爬虫字段定义
class DazhongdianpingItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    CityName = scrapy.Field()  #
    CityId = scrapy.Field()  #
    CityPinYin = scrapy.Field()  #
    CategoryId = scrapy.Field()  #
    CategoryName = scrapy.Field()  #
    CategoryEnName = scrapy.Field()  #
    tagName = scrapy.Field()  #
    tagUrl = scrapy.Field()  #
    tagId = scrapy.Field()  #
    detailUrl = scrapy.Field()  # 详情页
    ShopNames = scrapy.Field()  #
    ShopdimatchText = scrapy.Field()  #
    ShopdiregionName = scrapy.Field()  #
    ShopHref = scrapy.Field()  #

    place = scrapy.Field()  #
    phone = scrapy.Field()  #
    Image = scrapy.Field()  #
    ShopName = scrapy.Field()  #
    Start = scrapy.Field()  #
    CommentNum = scrapy.Field()  #
    Average = scrapy.Field()  #
    Desc = scrapy.Field()  #
    other = scrapy.Field()  #
    body = scrapy.Field()
