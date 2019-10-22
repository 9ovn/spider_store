# -*- coding: utf-8 -*-
import scrapy
from sinacrawl.items import SinacrawlItem
from redis import Redis

Cookies = Redis('你的ip', '你的端口').get('账号')

class WeibocrawlSpider(scrapy.Spider):

    name = 'weibocrawl'
    allowed_domains = ['weibo.com']
    page_num = 0
    start_urls = 'https://weibo.cn/comment/hot/Hx1gulh4A?rl=1&oid=4378696905070520&page=1'
    cookies = cookies
    def start_requests(self):
        print(1)
        yield scrapy.Request(url=self.start_urls, callback=self.parse, cookies=self.cookies)

    def parse(self, response):
        """
        第一页抓取获取page
        :param response:
        :return:
        """
        url = f'https://weibo.cn/comment/hot/Hx1gulh4A?rl=1&oid=4378696905070520&page={self.page_num}'
        page = response.selector.css('[value]').re_first(r'(\d+)')
        print(page)

        try:
            print(2)
            while self.page_num < int(page):
                print(3)
                self.page_num += 1
                url = f'https://weibo.cn/comment/hot/Hx1gulh4A?rl=1&oid=4378696905070520&page={self.page_num}'
                print(5)
                yield scrapy.Request(url=url, callback=self.commen_parse, cookies=self.cookies, dont_filter=True )
            return None
        except Exception as eRR:
            print(7)
            raise eRR

    def commen_parse(self, response):
        """
        抓取评论
        :param response:
        :return:
        """
        item = SinacrawlItem()

        try:
            comment = response.xpath(r'//div[@class="c"]/span[1]/text()').extract()
            like = response.xpath(r'//div[@class="c"]/span[2]/a/text()').extract() # [i][2:-1]
            user_id = response.xpath(r'//*[@class="c"]/@id').extract() # [i] [2:]
            for i in range(10):
                try:
                    item['comment'] = comment[i]
                    item['like'] = like[i][2:-1]
                    item['user_id'] = user_id[i]
                except IndexError:
                    item['none'] = '没有数据'

                yield item

        except Exception as ERR:
            raise ERR
