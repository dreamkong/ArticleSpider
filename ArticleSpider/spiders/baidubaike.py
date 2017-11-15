# -*- coding: utf-8 -*-
import scrapy


class BaidubaikeSpider(scrapy.Spider):
    name = 'baidubaike'
    allowed_domains = ['baike.baidu.com']
    start_urls = ['http://baike.baidu.com/']

    def parse(self, response):
        pass
