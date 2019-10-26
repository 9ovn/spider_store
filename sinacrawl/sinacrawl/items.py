# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Field, Item


class SinacrawlItem(Item):

    collection = 'weibo_info'

    like = Field()
    comment = Field()
    user_id = Field()
    none = Field()
