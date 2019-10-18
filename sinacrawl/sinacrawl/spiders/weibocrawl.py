# -*- coding: utf-8 -*-
import scrapy


class WeibocrawlSpider(scrapy.Spider):
    name = 'weibocrawl'
    allowed_domains = ['m.weibo.com']
    start_urls = ['http://m.weibo.com/']

    def parse(self, response):
        pass
