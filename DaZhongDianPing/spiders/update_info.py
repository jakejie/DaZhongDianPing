# -*- coding:utf-8 -*-
__author__ = "jake"
__email__ = "jakejie@163.com"
"""
Project:DaZhongDianPing
FileName = PyCharm
Version:1.0
CreateDay:2018/7/4 14:20
"""
import re
import scrapy
from DaZhongDianPing.pipelines import BusinessInfo
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from DaZhongDianPing.settings import db_host, db_user, db_pawd, db_name, db_port

# 创建对象的基类:
Base = declarative_base()

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


class CrawlNoneSpider(scrapy.Spider):
    name = 'business_update'
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
        'CONCURRENT_REQUESTS': 1,
        # 'DOWNLOAD_DELAY': 3,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'CONCURRENT_REQUESTS_PER_IP': 1,
        'DOWNLOAD_TIMEOUT': 10,
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'DaZhongDianPing.middlewares.ProxyMiddleware': 110,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': 120,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 130,
        },
        # 'ITEM_PIPELINES': {
        #     'DaZhongDianPing.pipelines.DazhongdianpingPipeline': 300,
        # },
    }

    def __init__(self):
        engine = create_engine('mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8mb4'
                               .format(db_user, db_pawd, db_host, db_port, db_name), max_overflow=5000,
                               pool_recycle=3600, pool_size=5000, pool_timeout=3600)
        # 创建DBSession类型:
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()
        # self.num = 0

    # 提取所有空的店铺信息
    def start_requests(self):
        result = self.session.query(BusinessInfo).filter_by(phone='').limit(1)
        for data in result:
            url = data.ShopHref
            id = data.id
            Image = data.Image
            times = 0
            yield scrapy.Request(url, callback=self.parse_item,
                                 meta={"id": id, "Image": Image, "times": times},
                                 dont_filter=True)

    # 处理数据
    def parse_item(self, response):
        id = response.meta["id"]
        item = {}
        item["Image"] = response.meta["Image"]
        place = "".join(response.xpath('//*[@id="basic-info"]/div[2]/span[2]/text()|\
                                        //*[@id="J_boxDetail"]/div/p[@class="shop-contact address"]/text()|\
                                        //*[@id="basic-info"]/div[@class="expand-info address"]/span/text()|\
                                        //*[@id="basic-info"]/div[@class="expand-info address"]/a/span/text()|\
                                                //*[@id="address"]/text()').extract())  # 地理位置
        address = "".join(re.findall(re.compile(r' address: "(.*?)", public'), response.text))
        # print("Place:{}   Address:{}".format(place, address))
        item["place"] = address if address else place
        item["phone"] = "".join(response.xpath('//*[@id="basic-info"]/p/span[2]/text()').extract())  # 手机号码
        if item["phone"] == "":
            item["phone"] = "".join(response.xpath('//*[@id="basic-info"]/p/text()').extract())  # 手机号码
            if item["phone"] == "":
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
        item["CommentNum"] = "".join(response.xpath('//*[@id="reviewCount"]/text()').extract())  # 评论数
        item["Average"] = "".join(response.xpath('//*[@id="avgPriceTitle"]/text()|\
                                                //div[@class="brief-info"]/span[1]/text()').extract())
        item["Desc"] = "/".join(response.xpath('//*[@id="comment_score"]/span/text()|\
                                                //div[@class="brief-info"]/span/text()').extract())  # 口味/环境/服务 评分
        item["other"] = "".join(response.xpath('//*[@id="basic-info"]/div[4]/p[1]/span[2]/text()').extract())
        # print(item)
        self.update_data(id=id, item=item)
        return item

    # 更新数据
    def update_data(self, id, item):
        result = self.session.query(BusinessInfo).filter_by(id=id).first()
        result.place = item["place"]
        result.phone = item["phone"]
        result.Image = item["Image"]
        result.ShopName = item["ShopName"]
        result.Start = item["Start"]
        result.CommentNum = item["CommentNum"]
        result.Average = item["Average"]
        result.Desc = item["Desc"]
        result.other = item["other"]
        # self.num = self.num + 1
        # if self.num == 100000:
        self.session.commit()
        print("数据更新完成 ID = {} ITEM = {}".format(id, item))
        # self.num = 0


if __name__ == "__main__":
    pass
