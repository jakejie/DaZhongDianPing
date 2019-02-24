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
    "Host": "www.dianping.com",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
}


class DpSpider(scrapy.Spider):
    name = 'business'
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
        'DOWNLOAD_TIMEOUT': 60,
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
        count = 6000000  # 偏移量
        num = 1000000  # 每次提取数量
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
            place = "".join(response.xpath('//*[@id="basic-info"]/div[2]/span[2]/text()|\
                                            //div[@class="address"]/text()|\
                                            //*[@id="J_boxDetail"]/div/p[@class="shop-contact address"]/text()|\
                                            //p[@class="shop-contact address"]/text()|\
                                            //*[@id="basic-info"]/div[@class="expand-info address"]/span/text()|\
                                            //*[@id="basic-info"]/div[@class="expand-info address"]/a/span/text()|\
                                                    //*[@id="address"]/text()').extract())  # 地理位置
            address = "".join(re.findall(re.compile(r' address: "(.*?)", public'), response.text))
            # print("Place:{}   Address:{}".format(place, address))
            item["place"] = address.replace(' ', '').replace('\n', '').replace('\t', '').replace('\r', '') \
                if address else \
                place.replace(' ', '').replace('\n', '').replace('\t', '').replace('\r', '')
            item["phone"] = "".join(response.xpath('//*[@id="basic-info"]/p/span[2]/text()|\
                                        //p[@class="expand-info tel"]/text()|\
                                        //p[@class="expand-info tel"]/span[@class="item"]/text()').extract())  # 手机号码
            if item["phone"].replace(' ', '') == "":
                item["phone"] = "".join(response.xpath('//*[@id="basic-info"]/p/text()').extract())  # 手机号码
                if item["phone"].replace(' ', '') == "":
                    item["phone"] = "".join(
                        response.xpath('//*[@id="J_boxDetail"]/div/div[3]/span/strong/text()').extract())
            if item["Image"] == "":
                item["Image"] = "".join(response.xpath('//*[@id="aside-photos"]/div/a/img/@src').extract())
                # 商家店铺主页图片
                if item["Image"] == "":
                    item["Image"] = "".join(response.xpath('//*[@id="J_boxReserve"]/div[1]/div[1]/img/@src').extract())
            item["ShopName"] = "".join(response.xpath('//*[@id="basic-info"]/h1/text()').extract())  # 商家店铺名字
            if item["ShopName"] == "":
                item["ShopName"] = "".join(response.xpath('//*[@id="J_boxDetail"]/div/div[1]/h1/text()').extract())
            item["Start"] = "".join(response.xpath('//*[@id="basic-info"]/div[1]/span[1]/@title').extract())  # 评分星数
            item["CommentNum"] = "".join(response.xpath('//*[@id="reviewCount"]/text()|\
                                    //div[@class="basic-info"]/div[2]/div[2]/div[1]/a/span/text()').extract())  # 评论数
            item["Average"] = "".join(response.xpath('//*[@id="avgPriceTitle"]/text()|\
                                                    //div[@class="brief-info"]/span[1]/text()').extract())
            item["Desc"] = "/".join(response.xpath('//*[@id="comment_score"]/span/text()|\
                                                    //div[@class="basic-info"]/div[2]/div[2]/div[1]/span/text()\
                                                    //div[@class="brief-info"]/span/text()').extract())  # 口味/环境/服务 评分
            item["other"] = "".join(response.xpath('//*[@id="basic-info"]/div[4]/p[1]/span[2]/text()|\
                                                    //p[@class="shop-contact"]/text()').extract())
            item["body"] = ""  # response.text
            # print(item)
            return item


def get_shop_href(url):
    href = "".join(re.findall(re.compile(r'shop/(\d+)'), url))
    url = "http://www.dianping.com/shop/{}".format(href)
    return url


def get_shop_list():
    pipeline = DazhongdianpingPipeline()
    result = pipeline.get_shop_list()
    for shop in result:
        get_shop_href(shop.ShopHref)
