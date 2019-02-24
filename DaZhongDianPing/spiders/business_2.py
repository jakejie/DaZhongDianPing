# -*- coding:utf-8 -*-
__author__ = "jake"
__email__ = "jakejie@163.com"
"""
获取大众点评的所有商户的详情数据

Project:美团大众点评数据
FileName = PyCharm
Version:1.0
CreateDay:2018/5/18 12:49
"""
import re
import scrapy
from DaZhongDianPing.pipelines import DazhongdianpingPipeline
from DaZhongDianPing.items import DazhongdianpingItem

shop_headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Host": "m.dianping.com",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)\
     Chrome/63.0.3239.132 Safari/537.36",
}


class DpSpider(scrapy.Spider):
    name = 'business_2'
    allowed_domains = ['dianping.com']
    custom_settings = {
        'BOT_NAME': 'DaZhongDianPing',
        'SPIDER_MODULES': ['DaZhongDianPing.spiders'],
        'NEWSPIDER_MODULE': 'DaZhongDianPing.spiders',
        'COOKIES_ENABLED': False,
        'REDIRECT_ENABLED': False,
        'ROBOTSTXT_OBEY': False,
        'RETRY_ENABLED': True,
        'RETRY_TIMES': 5,
        'RETRY_HTTP_CODECS': [500, 502, 503, 504, 408, 403, 400, 429, 302, 301],
        'HTTPERROR_ALLOWED_CODES': [400, 429, 500, 403],  # 上面报的是403，就把403加入
        'CONCURRENT_REQUESTS': 32,
        # 'DOWNLOAD_DELAY': 3,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 32,
        'CONCURRENT_REQUESTS_PER_IP': 32,
        'DOWNLOAD_TIMEOUT': 120,
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'DaZhongDianPing.middlewares.ProxyMiddleware': 110,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': 120,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 130,
        },
        'ITEM_PIPELINES': {
            'DaZhongDianPing.pipelines.DazhongdianpingPipeline': 300,
        },
    }

    # 起始页面 获取所有城市
    def start_requests(self):
        pipeline = DazhongdianpingPipeline()
        count = 5000000  # 偏移量
        num = 10  # 每次提取数量
        result = pipeline.get_shop_list(count, num)
        for shop in result:
            url = get_shop_href(shop.ShopHref)
            data = {
                "CityName": shop.CityName,
                "CityId": shop.CityId,
                "CityPinYin": shop.CityPinYin,
                "CategoryId": "",
                "CategoryName": shop.CategoryName,
                "CategoryEnName": "",
                "tagName": shop.tagName,
                "tagUrl": shop.tagUrl,
                "tagId": "",
                "detailUrl": shop.detailUrl,
                "ShopNames": shop.ShopNames,
                "ShopdimatchText": "",
                "ShopdiregionName": shop.ShopdiregionName,
                "ShopHref": url,
                "place": "",  #
                "phone": "",  #
                "Image": shop.Image,  #
                "ShopName": "",  #
                "Start": "",  #
                "CommentNum": "",  #
                "Average": "",  #
                "Desc": "",  #
                "other": "",  #
            }
            yield scrapy.Request(url, callback=self.parse_item,
                                 dont_filter=True,
                                 headers=shop_headers,
                                 meta=data)

    def parse_item(self, response):
        item = DazhongdianpingItem()
        item = response.meta
        if "抱歉！页面无法访问" in response.text:
            item["place"] = ""
            item["phone"] = ""
            item["Image"] = ""
            item["ShopName"] = ""
            item["Start"] = ""
            item["CommentNum"] = ""
            item["Average"] = ""
            item["Desc"] = ""
            item["other"] = ""
            item["body"] = response.text
            return item
        else:
            place = "".join(response.xpath('//div[@class="J_address"]/div/div/a/text()').extract())  # 地理位置
            address = "".join(re.findall(re.compile(r' address: "(.*?)","huiTime'), response.text))
            # print("Place:{}   Address:{}".format(place, address))
            item["place"] = address.replace(' ', '').replace('\n', '').replace('\t', '').replace('\r', '') \
                if address else \
                place.replace(' ', '').replace('\n', '').replace('\t', '').replace('\r', '')
            item["phone"] = "".join(
                response.xpath('//div[@class="J_phone"]/div/div/div/a/text()').extract()) \
                .replace(' ', '').replace('\n', '').replace('\t', '').replace('\r', '')  # 手机号码
            if item["phone"].replace(' ', '') == "":
                item["phone"] = "".join(response.xpath('//div[@class="J_phone"]/div/div/div/a/@href').extract()) \
                    .replace(' ', '').replace('\n', '').replace('\t', '').replace('\r', '')  # 手机号码
                if item["phone"].replace(' ', '').replace('tel:', '') == "":
                    item["phone"] = "".join(
                        re.findall(re.compile(r'"phoneNum":"(.*?)"}'), response.text))
            if item["Image"] == "":
                item["Image"] = "".join(response.xpath('//div[@class="J_baseinfo"]/div/a/img/@src').extract())
                # 商家店铺主页图片
                # if item["Image"] == "":
                #     item["Image"] = "".join(response.xpath('//*[@id="J_boxReserve"]/div[1]/div[1]/img/@src').extract())
            item["ShopName"] = "".join(
                response.xpath('//div[@class="J_baseinfo"]/div[@class="shopPicBg"]/h1/text()').extract())  # 商家店铺名字
            if item["ShopName"] == "":
                item["ShopName"] = "".join(
                    response.xpath('//div[@class="J_baseinfo"]/div/div/a/img/@alt').extract())
            item["Start"] = "".join(
                response.xpath(
                    '//div[@class="J_baseinfo"]/div/div[@class="shopPicBg"]/p/span[1]/@class').extract())  # 评分星数
            item["CommentNum"] = "".join(
                response.xpath('//div[@class="J_baseinfo"]/div/div[@class="shopPicBg"]/p/span[2]/span[1]/text()'
                               ).extract())  # 评论数
            item["Average"] = "".join(
                response.xpath('//div[@class="J_baseinfo"]/div/div[@class="shopPicBg"]/p/span[3]/text()').extract())
            item["Desc"] = "/".join(
                response.xpath(
                    '//div[@class="J_baseinfo"]/div/div[@class="desc"]/span/text()').extract())  # 口味/环境/服务 评分
            item["other"] = "".join(
                response.xpath('//div[@class="J_otherinfo"]/div[1]/div[1]/div[1]/text()').extract())
            item["body"] = ""  # response.text
            print(item)
            # return item


def get_shop_href(url):
    href = "".join(re.findall(re.compile(r'shop/(\d+)'), url))
    url = "http://m.dianping.com/shop/{}".format(href)
    return url


def get_shop_list():
    pipeline = DazhongdianpingPipeline()
    result = pipeline.get_shop_list()
    for shop in result:
        get_shop_href(shop.ShopHref)
