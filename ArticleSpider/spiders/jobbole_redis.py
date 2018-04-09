# -*- coding: utf-8 -*-
from urllib import parse

import scrapy
from scrapy.http import Request
from ArticleSpider.items import ArticleItemLoader, JobBoleArticleItem
from ArticleSpider.utils.common import get_md5
from scrapy_redis.spiders import RedisSpider


class JobboleRedisSpider(RedisSpider):
    name = 'jobbole_redis'
    allowed_domains = ['blog.jobbole.com']
    redis_key = 'jobbole_redis:start_urls'

    custom_settings = {
        "SCHEDULER": "scrapy_redis.scheduler.Scheduler",
        "DUPEFILTER_CLASS": "scrapy_redis.dupefilter.RFPDupeFilter",
        "ITEM_PIPELINES": {
            "scrapy_redis.pipelines.RedisPipeline": 300
        }
    }

    def parse(self, response):
        """
        1 获取文章列表页的文章url并交给解析函数解析
        2 获取下一页url并交给scrapy进行下载, 下载后交给parse
        """
        # post_urls = response.css('.floated-thumb .post-thumb > a::attr(href)').extract()
        # 解析列表页中的所有文章url并交给scrapy下载后并进行解析
        # post_urls = response.css('#archive > div.floated-thumb > div.post-thumb > a::attr(href)').extract()

        post_nodes = response.css('#archive > div.floated-thumb > div.post-thumb > a')
        for post_node in post_nodes:
            front_image_url = post_node.css('img::attr(src)').extract_first('')
            post_url = post_node.css('::attr(href)').extract_first('')
            yield Request(url=parse.urljoin(response.url, post_url), meta={'front_image_url': front_image_url},
                          callback=self.parse_detail)

        # 提取下一页并交给scrapy下载
        next_urls = response.css('.next.page-numbers::attr(href)').extract_first('')
        if next_urls:
            yield Request(url=parse.urljoin(response.url, next_urls), callback=self.parse)

    def parse_detail(self, response):
        # 通过item loader加载item
        front_image_url = response.meta.get("front_image_url", "")  # 文章封面图
        item_loader = ArticleItemLoader(item=JobBoleArticleItem(), response=response)
        item_loader.add_css("title", ".entry-header h1::text")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_css("create_date", "p.entry-meta-hide-on-mobile::text")
        item_loader.add_value("front_image_url", [front_image_url])
        item_loader.add_css("like_nums", ".vote-post-up h10::text")
        item_loader.add_css("comment_nums", "a[href='#article-comment'] span::text")
        item_loader.add_css("fav_nums", ".bookmark-btn::text")
        item_loader.add_css("tags", "p.entry-meta-hide-on-mobile a::text")
        item_loader.add_css("content", "div.entry")

        article_item = item_loader.load_item()

        yield article_item
