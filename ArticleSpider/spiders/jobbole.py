# -*- coding: utf-8 -*-
__author__ = 'dreamkong'

from urllib import parse

import scrapy
from scrapy.http import Request

from ArticleSpider.items import JobBoleArticleItem, ArticleItemLoader
from ArticleSpider.utils.common import get_md5


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

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

        # article_item = JobBoleArticleItem()
        # xpath()
        # title = response.xpath('//div[@class="entry-header"]/h1/text()').extract()[0]
        # create_date = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract()[0].replace('·','').strip()
        # like_nums = response.xpath('//span[contains(@class, "vote-post-up")]/h10/text()').extract()[0]
        # fav_nums = response.xpath('//span[contains(@class, "bookmark-btn")]/text()').extract()[0]
        # match_re = re.match('.*(\d).*',fav_nums)
        # if match_re:
        #     fav_nums = match_re.group(1)
        # comment_nums = response.xpath('//a[@href="#article-comment"]/span/text()').extract()[0]
        # match_re = re.match('.*(\d).*', comment_nums)
        # if match_re:
        #     comment_nums = match_re.group(1)
        #
        # content = response.xpath('//div[@class="entry"]').extract()[0]
        # tag_list = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/a/text()').extract()
        # tag_list = [ele for ele in tag_list if not ele.strip().endswith('评论')]
        # tags = ','.join(tag_list)

        # css选择器

        # front_image_url = response.meta.get('front_image_url','') # 文章封面图
        # css_title = response.css('div.entry-header > h1::text').extract()
        # css_create_date = response.css('p.entry-meta-hide-on-mobile::text').extract()[0].replace('·','').strip()
        #
        # css_like_nums = response.css('.vote-post-up h10::text').extract()[0]
        # match_re = re.match('.*(\d).*', css_like_nums)
        # if match_re:
        #     css_like_nums = int(match_re.group(1))
        # else:
        #     css_like_nums = 0
        # css_fav_nums = response.css('.bookmark-btn::text').extract()[0]
        # match_re = re.match('.*(\d).*', css_fav_nums)
        # if match_re:
        #     css_fav_nums = int(match_re.group(1))
        # else:
        #     css_fav_nums = 0
        # css_comment_nums = response.css('a[href = "#article-comment"] > span::text').extract()[0]
        # match_re = re.match('.*(\d).*', css_comment_nums)
        # if match_re:
        #     css_comment_nums = int(match_re.group(1))
        # else:
        #     css_comment_nums = 0
        #
        # css_content = response.css('div.entry').extract()[0]
        # css_tag_list = response.css('p.entry-meta-hide-on-mobile a::text').extract()
        # css_tag_list = [ele for ele in css_tag_list if not ele.strip().endswith('评论')]
        # css_tags = ','.join(css_tag_list)
        #
        # article_item['url_object_id'] = get_md5(response.url)
        # article_item['title'] = css_title
        # article_item['url'] = response.url
        # try:
        #     css_create_date = datetime.datetime.strptime(css_create_date,'%Y/%m/%d').date()
        # except Exception as e:
        #     css_create_date = datetime.datetime.now().date()
        #
        # article_item['create_date'] = css_create_date
        # article_item['front_image_url'] = [front_image_url]
        # article_item['like_nums'] = css_like_nums
        # article_item['comment_nums'] = css_comment_nums
        # article_item['fav_nums'] = css_fav_nums
        # article_item['tags'] = css_tags
        # article_item['content'] = css_content

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
