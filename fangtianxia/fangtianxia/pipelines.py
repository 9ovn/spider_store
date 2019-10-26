# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from fangtianxia.items import NewHouseItem, OldHouseItem


# class NewMongoPipeline(object):
#     def __init__(self, mongo_uri, mongo_db):
#         self.mongo_uri = mongo_uri
#         self.mongo_db = mongo_db
#
#     @classmethod
#     def from_crawler(cls, crawler):
#         return cls(
#             mongo_uri=crawler.settings.get('MONGO_URI'),
#             mongo_db=crawler.settings.get('MONGO_DB')
#         )
#
#     def open_spider(self, spider):
#         self.client = pymongo.MongoClient(self.mongo_uri)
#         self.db = self.client[self.mongo_db]
#
#     def process_item(self, item, spider):
#         name = item.__class__.__name__
#         if isinstance(item, NewHouseItem):
#             try:
#                 self.db[name].insert(dict(item))
#                 return item
#             except Exception as Err:
#                 print(Err)
#
#     def close_spider(self, spider):
#         self.client.close()
#
# class OldMongoPipeline(object):
#     def __init__(self, mongo_uri, mongo_db):
#         self.mongo_uri = mongo_uri
#         self.mongo_db = mongo_db
#
#     @classmethod
#     def from_crawler(cls, crawler):
#         return cls(
#             mongo_uri=crawler.settings.get('MONGO_URI'),
#             mongo_db=crawler.settings.get('MONGO_DB')
#         )
#
#     def open_spider(self, spider):
#         self.client = pymongo.MongoClient(self.mongo_uri)
#         self.db = self.client[self.mongo_db]
#
#
#     def process_item(self, item, spider):
#         name = item.__class__.__name__
#         if isinstance(item, OldHouseItem):
#             try:
#                 self.db[name].insert(dict(item))
#                 return item
#             except Exception as Err:
#                 print(Err)
#
#
#     def close_spider(self, spider):
#         self.client.close()
class MongodbPipeline(object):
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.db[NewHouseItem.collection].create_index([('id', pymongo.ASCENDING)])
        self.db[OldHouseItem.collection].create_index([('id', pymongo.ASCENDING)])
        print("打开数据库...")

    def close_spider(self,spider):
        print('写入完毕，关闭数据库.')
        self.client.close()

    def process_item(self, item, spider):
        if isinstance(item, NewHouseItem):
            self.db[item.collection].update( {'$set': dict(item)}, True)
        elif isinstance(item, OldHouseItem):
            self.db[item.collection].update({'$set': dict(item)}, True)
        print('正在写入...')
        return item