# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class NewHouseItem(Item):
    collection = 'NewHouse'
    # 市
    city = Field()
    # 楼盘位置
    location = Field()
    # 楼盘名字
    real_estate = Field()
    # 楼盘面积
    type = Field()
    # 在售与否
    status = Field()
    # 楼盘均价
    price = Field()


class OldHouseItem(Item):
    collection = 'OldHouse'
    # 市
    city = Field()
    # 楼盘名
    title = Field()
    # 楼盘位置
    location = Field()
    # 价格
    price = Field()
    pre_price = Field()
    # 详细信息
    info = Field()
