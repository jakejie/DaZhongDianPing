# -*- coding:utf-8 -*-
__author__ = "jake"
__email__ = "jakejie@163.com"
"""
获取大众点评的所有分类下的商户列表

Project:美团大众点评数据
FileName = PyCharm
Version:1.0
CreateDay:2018/5/18 12:49
"""
import re
import scrapy
from DaZhongDianPing.items import DazhongdianpingItem
from .cityInfo import citys

# CRAWLDETAIL = True  # True表示获取详情页数据
CRAWLDETAIL = False  # False表示不获取详情页数据
headers = {
    "Host": "www.dianping.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
}
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
    name = 'dp'
    allowed_domains = ['dianping.com']
    custom_settings = {
        'BOT_NAME': 'DaZhongDianPing',
        'SPIDER_MODULES': ['DaZhongDianPing.spiders'],
        'NEWSPIDER_MODULE': 'DaZhongDianPing.spiders',
        'ROBOTSTXT_OBEY': False,
        # 'DUPEFILTER_DEBUG': False,  # 记录所有重复的请求
        'RETRY_ENABLED': True,
        'RETRY_TIMES': 5,
        'RETRY_HTTP_CODECS': [500, 502, 503, 504, 408, 403, 400, 429, 302, 301],
        'REDIRECT_ENABLED': False,  # 禁止重定向
        'REDIRECT_MAX_TIMES': 20,  # 定义请求可重定向的最长时间。在此最大值之后，请求的响应被原样返回。我们对同一个任务使用Firefox默认值
        'REDIRECT_PRIORITY_ADJUST': +2,  # 相对于原始请求调整重定向请求优先级：正优先级调整（默认）意味着更高的优先级。负优先级调整意味着较低优先级。
        # HTTPERROR_ALLOWED_CODES = [400, 429, 500, 403]  # 上面报的是403，就把403加入
        'CONCURRENT_REQUESTS': 300,
        'CONCURRENT_ITEMS': 100,  # 在项处理器（也称为项目管道）中并行处理的并发项目的最大数量（每个响应）
        'COOKIES_ENABLED': False,
        'DOWNLOAD_TIMEOUT': 60,
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'DaZhongDianPing.middlewares.ProxyMiddleware': 110,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': 120,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 130,
            'scrapy.contrib.downloadermiddleware.redirect.RedirectMiddleware': 600,
        },
        'ITEM_PIPELINES': {
            'DaZhongDianPing.pipelines.DazhongdianpingPipeline': 300,
        },
    }

    # 起始页面 获取所有城市
    def start_requests(self):
        for city in citys:
            # CityHref = city[0]
            CityName = city[1]
            CityId = city[2]
            CityPinYin = city[3]
            # CityName = "北京"
            # CityPinYin = "beijing"
            # CityId = ""
            CityHref = "http://www.dianping.com/{}".format(CityPinYin)
            if CityPinYin != "beijing":
                yield scrapy.Request(CityHref, callback=self.parse_category,
                                     headers=headers,
                                     meta={"CityName": CityName,
                                           "CityId": CityId,
                                           "CityPinYin": CityPinYin})

    # 获取分类
    def parse_category(self, response):
        category_list = response.xpath('//ul[@class="first-cate J-primary-menu"]/li')
        for categorys in category_list:
            category = "".join(categorys.xpath('div[1]/span/a[1]/text()').extract())
            tag_list = categorys.xpath('div[2]/div[1]/div/div[2]/a')
            for tag in tag_list:
                href = "".join(tag.xpath('@href').extract())
                name = "".join(tag.xpath('text()').extract())
                if "search" in href or "dianping.com" not in href:
                    pass
                else:
                    headers2 = {
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                        "Accept-Encoding": "gzip, deflate",
                        "Accept-Language": "zh-CN,zh;q=0.9",
                        "Cache-Control": "max-age=0",
                        "Connection": "keep-alive",
                        "Host": "www.dianping.com",
                        "Referer": response.url,
                        "Upgrade-Insecure-Requests": "1",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
                    }
                    yield scrapy.Request(href, callback=self.parse_area,
                                         headers=headers2,
                                         dont_filter=True,
                                         meta={
                                             "CategoryName": category,
                                             "CityId": response.meta["CityId"],
                                             "CityName": response.meta['CityName'],
                                             "CityPinYin": response.meta["CityPinYin"],
                                             "tagName": name,
                                             "tagUrl": href,
                                         })

    # 获取地域
    def parse_area(self, response):
        # print("获取地区===")
        areas = response.xpath('//*[@id="J_shopsearch"]/div[2]/div/ul/li/a|//*[@id="region-nav"]/a')
        for area in areas:
            href = "".join(area.xpath('@href').extract())
            name = "".join(area.xpath('text()|span/text()').extract())
            if "http" not in href:
                href = "http:" + href
            if "更多" in name or "收起" in name or "dianping.com" not in href:
                pass
            else:
                # print(href, name)
                yield scrapy.Request(href, callback=self.parse_detail,
                                     headers=headers,  # dont_filter=True,
                                     meta={
                                         "CategoryName": response.meta["CategoryName"],
                                         "CityId": response.meta["CityId"],
                                         "CityName": response.meta["CityName"],
                                         "CityPinYin": response.meta["CityPinYin"],
                                         "tagName": response.meta["tagName"],
                                         "tagUrl": response.meta["tagUrl"],
                                         "ShopdiregionName": name,

                                     })

    # 处理详情列表
    def parse_detail(self, response):
        try:
            all_page = int("".join(response.xpath('//*[@id="J_boxlist"]/div[3]/div/a[last()-1]/text()|\
                                                 //div[@class="page"]/a[last()-1]/text()').extract()))
            print("总页数：{}".format(all_page))
        # 有可能是response出错 有可能没有下一页
        except Exception as e:
            print("获取总页码出错：{}".format(e))
            # yield scrapy.Request(response.url, callback=self.parse_detail,
            #                      headers=headers,  # dont_filter=True,
            #                      meta=response.meta)
            all_page = 49
        if all_page == 50:
            area_list = response.xpath('//*[@id="region-nav-sub"]/a')
            for area in area_list[1:]:
                href = "".join(area.xpath('@href').extract())
                name = "".join(area.xpath('text()|span/text()').extract())
                if "http" not in href:
                    href = "http:" + href
                if "更多" in name or "收起" in name or "dianping.com" not in href:
                    pass
                else:
                    # print(href, name)
                    yield scrapy.Request(href, callback=self.parse_detail2,
                                         headers=headers, dont_filter=True,
                                         meta={
                                             "CategoryName": response.meta["CategoryName"],
                                             "CityId": response.meta["CityId"],
                                             "CityName": response.meta["CityName"],
                                             "CityPinYin": response.meta["CityPinYin"],
                                             "tagName": response.meta["tagName"],
                                             "tagUrl": response.meta["tagUrl"],
                                             "ShopdiregionName": response.meta["ShopdiregionName"] + "/" + name,

                                         })
        else:
            shops = response.xpath('//*[@id="J_boxlist"]/div[2]/li|\
                                 //*[@id="shop-all-list"]/ul/li')
            for shop in shops:
                if CRAWLDETAIL:
                    item = DazhongdianpingItem()
                href = "".join(shop.xpath('a/@href|div[2]/div[1]/a/@href').extract())
                image = "".join(shop.xpath('a/img/@src|div[1]/a/img/@src').extract())
                name = "".join(shop.xpath('div[1]/div[1]/div[1]/h3/a/text()|\
                                           div[2]/div[1]/a/h4/text()').extract())
                if href.startswith("//"):
                    href = "http:" + href
                if CRAWLDETAIL:
                    shop_id = "".join(re.findall(re.compile(r'shop/([0-9]{1,20})'), href))
                    url = "http://www.dianping.com/shop/{}".format(shop_id)
                    yield scrapy.Request(url, callback=self.shop_info,
                                         headers=shop_headers,
                                         meta={
                                             "CategoryName": response.meta["CategoryName"],
                                             "CityId": response.meta["CityId"],
                                             "CityName": response.meta["CityName"],
                                             "CityPinYin": response.meta["CityPinYin"],
                                             "tagName": response.meta["tagName"],
                                             "tagUrl": response.meta["tagUrl"],
                                             "ShopdiregionName": response.meta["ShopdiregionName"],
                                             "detailUrl": response.url,
                                             "Image": image,
                                             "ShopNames": name
                                         })
                else:
                    item = {
                        "CityName": response.meta["CityName"],
                        "CityId": response.meta["CityId"],
                        "CityPinYin": response.meta["CityPinYin"],
                        "CategoryId": "",
                        "CategoryName": response.meta["CategoryName"],
                        "CategoryEnName": "",
                        "tagName": response.meta["tagName"],
                        "tagUrl": response.meta["tagUrl"],
                        "tagId": "",
                        "detailUrl": response.url,
                        "ShopNames": name,
                        "ShopdimatchText": "",
                        "ShopdiregionName": response.meta["ShopdiregionName"],
                        "ShopHref": href,
                        "place": "",  #
                        "phone": "",  #
                        "Image": image,  #
                        "ShopName": "",  #
                        "Start": "",  #
                        "CommentNum": "",  #
                        "Average": "",  #
                        "Desc": "",  #
                        "other": "",  #
                    }
                    yield item
            nextPage = response.xpath('//*[@id="J_boxlist"]/div[3]/div/a[@class="nextPage"]/@href|\
                        //div[@class="page"]/a[@class="next"]/@href').extract()
            if nextPage:
                if "www.dianping.com" in "".join(nextPage):
                    urls = "".join(nextPage)
                else:
                    urls = "http://www.dianping.com" + "".join(nextPage)
                print("下一页：{}".format(urls))
                yield scrapy.Request(urls, callback=self.parse_detail,
                                     headers=headers,
                                     meta={
                                         "CategoryName": response.meta["CategoryName"],
                                         "CityId": response.meta["CityId"],
                                         "CityName": response.meta["CityName"],
                                         "CityPinYin": response.meta["CityPinYin"],
                                         "tagName": response.meta["tagName"],
                                         "tagUrl": response.meta["tagUrl"],
                                         "ShopdiregionName": response.meta["ShopdiregionName"],
                                     })

    # 若详情页列表分类页码大于50 再细分
    def parse_detail2(self, response):
        shops = response.xpath('//*[@id="J_boxlist"]/div[2]/li|\
                                         //*[@id="shop-all-list"]/ul/li')
        for shop in shops:
            if CRAWLDETAIL:
                item = DazhongdianpingItem()
            href = "".join(shop.xpath('a/@href|div[2]/div[1]/a/@href').extract())
            image = "".join(shop.xpath('a/img/@src|div[1]/a/img/@src').extract())
            name = "".join(shop.xpath('div[1]/div[1]/div[1]/h3/a/text()|\
                                                   div[2]/div[1]/a/h4/text()').extract())
            if href.startswith("//"):
                href = "http:" + href
            if CRAWLDETAIL:
                shop_id = "".join(re.findall(re.compile(r'shop/([0-9]{1,20})'), href))
                url = "http://www.dianping.com/shop/{}".format(shop_id)
                yield scrapy.Request(url, callback=self.shop_info,
                                     headers=shop_headers,
                                     meta={
                                         "CategoryName": response.meta["CategoryName"],
                                         "CityId": response.meta["CityId"],
                                         "CityName": response.meta["CityName"],
                                         "CityPinYin": response.meta["CityPinYin"],
                                         "tagName": response.meta["tagName"],
                                         "tagUrl": response.meta["tagUrl"],
                                         "ShopdiregionName": response.meta["ShopdiregionName"],
                                         "detailUrl": response.url,
                                         "Image": image,
                                         "ShopNames": name
                                     })
            else:
                item = {
                    "CityName": response.meta["CityName"],
                    "CityId": response.meta["CityId"],
                    "CityPinYin": response.meta["CityPinYin"],
                    "CategoryId": "",
                    "CategoryName": response.meta["CategoryName"],
                    "CategoryEnName": "",
                    "tagName": response.meta["tagName"],
                    "tagUrl": response.meta["tagUrl"],
                    "tagId": "",
                    "detailUrl": response.url,
                    "ShopNames": name,
                    "ShopdimatchText": "",
                    "ShopdiregionName": response.meta["ShopdiregionName"],
                    "ShopHref": href,
                    "place": "",  #
                    "phone": "",  #
                    "Image": image,  #
                    "ShopName": "",  #
                    "Start": "",  #
                    "CommentNum": "",  #
                    "Average": "",  #
                    "Desc": "",  #
                    "other": "",  #
                }
                yield item
        nextPage = response.xpath('//*[@id="J_boxlist"]/div[3]/div/a[@class="nextPage"]/@href|\
                                //div[@class="page"]/a[@class="next"]/@href').extract()
        if nextPage:
            if "www.dianping.com" in "".join(nextPage):
                urls = "".join(nextPage)
            else:
                urls = "http://www.dianping.com" + "".join(nextPage)
            print("下一页：{}".format(urls))
            yield scrapy.Request(urls, callback=self.parse_detail2,
                                 headers=headers,
                                 meta={
                                     "CategoryName": response.meta["CategoryName"],
                                     "CityId": response.meta["CityId"],
                                     "CityName": response.meta["CityName"],
                                     "CityPinYin": response.meta["CityPinYin"],
                                     "tagName": response.meta["tagName"],
                                     "tagUrl": response.meta["tagUrl"],
                                     "ShopdiregionName": response.meta["ShopdiregionName"],
                                 })

    # 解析店铺详情页数据
    def shop_info(self, response):
        print("处理详情页====")
        item = DazhongdianpingItem()
        place = "".join(response.xpath('//*[@id="basic-info"]/div[2]/span[2]/text()').extract())  # 地理位置
        phone = "".join(response.xpath('//*[@id="basic-info"]/p/span[2]/text()').extract())  # 手机号码
        if phone == "":
            phone = "".join(response.xpath('//*[@id="basic-info"]/p/text()').extract())  # 手机号码
        Image = "".join(response.xpath('//*[@id="aside-photos"]/div/a/img/@src').extract())  # 商家店铺主页图片
        ShopName = "".join(response.xpath('//*[@id="basic-info"]/h1/text()').extract())  # 商家店铺名字
        Start = "".join(response.xpath('//*[@id="basic-info"]/div[1]/span[1]/@title').extract())  # 评分星数
        CommentNum = "".join(response.xpath('//*[@id="reviewCount"]/text()').extract())  # 评论数
        Average = "".join(response.xpath('//*[@id="avgPriceTitle"]/text()').extract())
        Desc = "/".join(response.xpath('//*[@id="comment_score"]/span/text()').extract())  # 口味/环境/服务 评分
        other = "".join(response.xpath('//*[@id="basic-info"]/div[4]/p[1]/span[2]/text()').extract())
        item = {
            "CityName": response.meta["CityName"],
            "CityId": response.meta["CityId"],
            "CityPinYin": response.meta["CityPinYin"],
            "CategoryId": "",
            "CategoryName": response.meta["CategoryName"],
            "CategoryEnName": "",
            "tagName": response.meta["tagName"],
            "tagUrl": response.meta["tagUrl"],
            "tagId": "",
            "detailUrl": response.meta["detailUrl"],
            "ShopNames": response.meta["ShopNames"],
            "ShopdimatchText": "",
            "ShopdiregionName": response.meta["ShopdiregionName"],
            "ShopHref": response.url,
            "place": place,  #
            "phone": phone,  #
            "Image": response.meta["Image"] if response.meta["Image"] else Image,  #
            "ShopName": ShopName,  #
            "Start": Start,  #
            "CommentNum": CommentNum,  #
            "Average": Average,  #
            "Desc": Desc,  #
            "other": other,  #
        }
        return item
