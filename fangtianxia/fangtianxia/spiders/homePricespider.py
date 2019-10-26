# -*- coding: utf-8 -*-
import scrapy, re
from fangtianxia.items import NewHouseItem, OldHouseItem
import logging
# from scrapy_redis.spiders import RedisSpider

# 若部署分布式则将scrapy.Spider替换为RedisSpider
class HomepricespiderSpider(scrapy.Spider):
    name = 'homePricespider'
    allowed_domains = ['fang.com']
    start_urls = ['https://www.fang.com/SoufunFamily.htm']
    # redis_key = 'fangtianxia:start_url'

    def parse(self, response):
        trs = response.xpath(r"//div[@class='outCont']//tr/td")[0:-2]
        for tr in trs:
            city_links = tr.xpath(".//a")
            for city_link in city_links:
                city_name = city_link.xpath(".//text()").get()
                city_url = city_link.xpath(".//@href").get()
                if "bj." in city_url:
                    newhouse = "https://newhouse.fang.com/"
                    oldhouse = "https://esf.fang.com/"

                else:
                    url_s = city_url.split(".")
                    first, second, third = url_s[0], url_s[1], url_s[2]
                    first = re.sub('http', 'https', first)
                    newhouse = first + ".newhouse." + second + "." + third + 'house/s/'
                    oldhouse = first + ".esf." + second + "." + third

                    yield scrapy.Request(url=newhouse, callback=self.newhouse_parse, meta={"name": (city_name)})
                    yield scrapy.Request(url=oldhouse, callback=self.oldhouse_parse, meta={"name": (city_name)})

    def newhouse_parse(self, response):
        item = NewHouseItem()
        city_name = response.meta.get('name')

        try:
            divs = response.xpath(r'//div[@class="nhouse_list"]//li//div[@class="clearfix"]')
            for div in divs:
                item['city'] = city_name
                item['location'] = div.xpath(r'.//div[@class="address"]/a/@title').extract_first()
                item['real_estate'] = div.xpath(r'.//a[@target="_blank"]//img/@alt').extract_first()
                type = div.xpath(r'string(.//div[@class="house_type clearfix"])').extract_first()
                item['type'] = re.sub(r'\s', '', type)
                item['status'] = div.xpath(r'.//div[@class="nlc_details"]/div[4]/span/text()').extract_first()
                item['price'] = div.xpath(r'string(.//div[@class="nhouse_price"])').extract_first().strip()
                yield item

            next_page = response.xpath(r'//*[@id="sjina_C01_47"]/ul/li[2]/a[@class="next"]/@href').extract_first()
            if next_page:
                yield scrapy.Request(url=response.urljoin(next_page),
                                     callback=self.newhouse_parse,
                                     meta={"name": (city_name)}
                                     )
            else:
                print('最后一页')
        except Exception as Err:
            logger = logging.getLogger(__name__)
            logger.debug('新房子爬虫出点错误' + str(Err))


    def oldhouse_parse(self, response):
        item = OldHouseItem()
        city_name = response.meta.get('info')

        try:
            dds = response.xpath(r'//dl[@class="clearfix"]')
            for dd in dds:
                item['title'] = dd.xpath(r'.//dd/h4/a/@title').extract_first()
                info = dd.xpath(r'string(.//dd/p)').extract_first()
                item['info'] = re.sub(r'\s', '', info)
                item['price'] = dd.xpath(r'.//dd//span//b/text()').extract_first()
                item['pre_price'] = dd.xpath(r'.//dd[@class="price_right"]//span[not(@class)]//text()').extract_first()
                item['location'] = dd.xpath(r'.//dd//p[@class="add_shop"]/span/text()').extract_first()
                yield item

            next_page = response.xpath(r'//div[@class="page_al"]//p[last()-2]/a/@href').extract_first()

            if next_page:
                yield scrapy.Request(url=response.urljoin(next_page),
                                     callback=self.oldhouse_parse,
                                     meta={"name": (city_name)}
                                     )
            else:
                print('最后一页')
        except Exception as Err:
            logger = logging.getLogger(__name__)
            logger.debug('二手饭爬虫出点错误:' + str(Err))

