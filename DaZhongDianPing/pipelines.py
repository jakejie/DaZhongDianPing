# -*- coding: utf-8 -*-
from datetime import datetime
from sqlalchemy import Column, String, create_engine, Integer, DateTime, TEXT
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from DaZhongDianPing.settings import db_host, db_user, db_pawd, db_name, db_port

# 创建对象的基类:
Base = declarative_base()


# 商家基础信息
class BasicInfo(Base):
    __tablename__ = "shop"
    # 表结构
    id = Column(Integer, unique=True, primary_key=True)
    CityName = Column(String(256))  #
    CityId = Column(String(256))  #
    CityPinYin = Column(String(256))  #
    CategoryId = Column(String(256))  #
    CategoryName = Column(String(256))  #
    CategoryEnName = Column(String(256))  #
    tagName = Column(String(256))  #
    tagUrl = Column(String(256))  #
    tagId = Column(String(256))  #
    detailUrl = Column(String(512))
    ShopNames = Column(String(256))  #
    ShopdimatchText = Column(String(256))  #
    ShopdiregionName = Column(String(256))  #
    ShopHref = Column(String(256))  #

    place = Column(String(256))  #
    phone = Column(String(256))  #
    Image = Column(String(512))  #
    ShopName = Column(String(256))  #
    Start = Column(String(256))  #
    CommentNum = Column(String(256))  #
    Average = Column(String(256))  #
    Desc = Column(String(256))  #
    other = Column(String(256))  #

    add_time = Column(DateTime, default=datetime.now)


# 更新后的基本信息
class BusinessInfo(Base):
    __tablename__ = "business"
    # 表结构
    id = Column(Integer, unique=True, primary_key=True)
    CityName = Column(String(256))  #
    CityId = Column(String(256))  #
    CityPinYin = Column(String(256))  #
    CategoryId = Column(String(256))  #
    CategoryName = Column(String(256))  #
    CategoryEnName = Column(String(256))  #
    tagName = Column(String(256))  #
    tagUrl = Column(String(256))  #
    tagId = Column(String(256))  #
    detailUrl = Column(String(512))
    ShopNames = Column(String(256))  #
    ShopdimatchText = Column(String(256))  #
    ShopdiregionName = Column(String(256))  #
    ShopHref = Column(String(256))  #

    place = Column(String(256))  #
    phone = Column(String(256))  #
    Image = Column(String(512))  #
    ShopName = Column(String(256))  #
    Start = Column(String(256))  #
    CommentNum = Column(String(256))  #
    Average = Column(String(256))  #
    Desc = Column(String(256))  #
    other = Column(String(256))  #
    body = Column(TEXT, default="")
    add_time = Column(DateTime, default=datetime.now)


class DazhongdianpingPipeline(object):
    def __init__(self):
        engine = create_engine('mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8mb4'
                               .format(db_user, db_pawd, db_host, db_port, db_name), max_overflow=5000,
                               pool_recycle=3600, pool_size=5000)
        # 创建DBSession类型:
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()

    def get_shop_list(self, offset, num):
        result = self.session.query(BasicInfo).offset(offset).limit(num)  # .all()  # .filter_by()
        return result

    def process_item(self, item, spider):
        info = BusinessInfo(
            CityName=item["CityName"],  # 城市名
            CityId=item["CityId"],  # 城市id
            CityPinYin=item["CityPinYin"],  # 城市拼音
            CategoryId=item["CategoryId"],  # 分类id
            CategoryName=item["CategoryName"],  # 分类名
            CategoryEnName=item["CategoryEnName"],  # 分类英文名
            tagName=item["tagName"],  # 标签名
            tagUrl=item["tagUrl"],  # 标签地址
            tagId=item["tagId"],  # 标签id
            detailUrl=item["detailUrl"],  # 详情地址
            ShopNames=item["ShopNames"],  # 店铺名
            ShopdimatchText=item["ShopdimatchText"],  #
            ShopdiregionName=item["ShopdiregionName"],  #
            ShopHref=item["ShopHref"],  # 店铺页面链接
            place=item["place"].replace('\n', ' ').replace('\t', ' ').replace('\r', ' '),  # 店铺地址
            phone=item["phone"].replace('\n', ' ').replace('\t', ' ').replace('\r', ' '),  # 店铺电话
            Image=item["Image"],  # 店铺图
            ShopName=item["ShopName"].replace('\n', ' ').replace('\t', ' ').replace('\r', ' '),  # 店铺名
            Start=item["Start"].replace('\n', ' ').replace('\t', ' ').replace('\r', ' '),  # 店铺星级
            CommentNum=item["CommentNum"].replace('\n', ' ').replace('\t', ' ').replace('\r', ' '),  # 店铺评论数
            Average=item["Average"].replace('\n', ' ').replace('\t', ' ').replace('\r', ' '),  # 店铺评分
            Desc=item["Desc"].replace('\n', ' ').replace('\t', ' ').replace('\r', ' '),  # 店铺描述
            other=item["other"].replace('\n', ' ').replace('\t', ' ').replace('\r', ' '),  # 其他
            body="",  #
            add_time=datetime.now(),
        )
        num = 0
        while True:
            num = num + 1
            try:
                self.session.add(info)
                self.session.commit()
                print("新插入：{}".format(item["ShopNames"]))
                print("插入成功".center(20, "*"))
                return item
            except Exception as e:
                print("[UUU] ShopNames Error :{}".format(e))
                self.session.rollback()


if __name__ == "__main__":
    engine = create_engine('mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'
                           .format(db_user, db_pawd, db_host, db_port, db_name), max_overflow=500)
    Base.metadata.create_all(engine)
