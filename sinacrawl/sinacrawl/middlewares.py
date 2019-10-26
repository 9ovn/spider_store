# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

import logging
from scrapy import signals
import requests
import redis



class ProxyMiddleware():
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_random_proxy(self):
        try:
            conn = redis.Redis(host='127.0.0.1', port='6379')
            ip = conn.srandmember('ip')
            status = requests.get('https://www.baidu.com').status_code
            if status == 200:
                return ip
        except Exception as Err:
            self.logger.debug('应该是IP出现了一些问题' + str(Err))
            return False

    def process_request(self, request, spider):
        if request.meta.get('retry_times'):
            proxy = self.get_random_proxy()
            if proxy:
                uri = 'https://{proxy}'.format(proxy=proxy)
                self.logger.debug('使用代理 ' + proxy)
                request.meta['proxy'] = uri


class CookiesMiddleware():
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_random_proxy(self):
        try:
            conn = redis.Redis(host='127.0.0.1', port='6379')
            cookies = conn.smembers('cookies')
            return cookies
        except Exception as Err:
            self.logger.debug('cookies出现了一些问题' + str(Err))
            return False

    def process_request(self, request, spider):
        self.logger.debug('正在获取Cookies')
        cookies = self.get_random_cookies()
        if cookies:
            request.cookies = cookies
            self.logger.debug('使用Cookies ' + str((cookies))