# -*- coding: utf-8 -*-

__author__ = 'dreamkong'

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import datetime
import re

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join

from ArticleSpider.utils.common import extract_nums
from ArticleSpider.settings import SQL_DATETIME_FORMAT, SQL_DATE_FORMAT


class ArticleSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def add_jobbole(value):
    return value + ' - jobbole'


def date_convert(value):
    value = value.replace('·', '').strip()
    try:
        create_date = datetime.datetime.strptime(value, '%Y/%m/%d').date()
    except Exception as e:
        create_date = datetime.datetime.now().date()

    return create_date


def get_nums(value):
    match_re = re.match('.*(\d).*', value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0
    return nums


def remove_comment_tags(value):
    # 去掉tag中提取的评论
    if "评论" in value:
        return ""
    else:
        return value


def return_value(value):
    return value


class ArticleItemLoader(ItemLoader):
    # 自定义ItemLoader
    default_output_processor = TakeFirst()


class JobBoleArticleItem(scrapy.Item):
    title = scrapy.Field(
        input_processor=MapCompose(add_jobbole)
    )
    create_date = scrapy.Field(
        input_processor=MapCompose(date_convert)
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(
        # imagePipeline 需要一个list
        output_processor=MapCompose(return_value)
    )
    front_image_path = scrapy.Field()
    like_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    comment_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    fav_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    tags = scrapy.Field(
        input_processor=MapCompose(remove_comment_tags),
        output_processor=Join(',')
    )
    content = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
                    insert into jobbole_articles(title, create_date, url, url_object_id, front_image_url, 
                    front_image_path,comment_nums,fav_nums, praise_nums, tags, content) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE comment_nums=VALUES(comment_nums), 
                    fav_nums=VALUES(fav_nums),praise_nums=VALUES(praise_nums)
                    """
        params = (self["title"], self["create_date"], self["url"], self['url_object_id'], self["front_image_url"],
                  self["front_image_path"], self["comment_nums"], self["fav_nums"], self["like_nums"],
                  self["tags"], self["content"])

        return insert_sql, params


class ZhihuQuestionItem(scrapy.Item):
    # 知乎的问题Item
    zhihu_id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answer_nums = scrapy.Field()
    comment_nums = scrapy.Field()
    watch_nums = scrapy.Field()
    click_nums = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
                    insert into zhihu_questions(zhihu_id, topics, url, title, content, 
                    answer_nums,comment_nums,watch_nums, click_nums, crawl_time) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE content=VALUES(content), 
                    answer_nums=VALUES(answer_nums),comment_nums=VALUES(comment_nums),watch_nums=VALUES(watch_nums),
                    click_nums=VALUES(click_nums)
                    """
        zhihu_id = int((self["zhihu_id"][0]))
        topics = ",".join(self['topics'])
        url = self['url'][0]
        title = "".join(self['title'])
        content = "".join(self['content'])
        answer_nums = extract_nums("".join(self['answer_nums']))
        comment_nums = extract_nums("".join(self['comment_nums']))
        watch_nums = extract_nums("".join(self['watch_nums'][0]))
        click_nums = extract_nums("".join(self['watch_nums'][1]))
        crawl_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)

        params = (zhihu_id, topics, url, title, content, answer_nums, comment_nums, watch_nums, click_nums, crawl_time)

        return insert_sql, params


class ZhihuAnswerItem(scrapy.Item):
    # 知乎的问题回答Item
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    praise_nums = scrapy.Field()
    comment_nums = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
                    insert into zhihu_answers(zhihu_id, url, question_id, author_id, 
                    content,praise_nums,comment_nums, create_time, update_time,crawl_time) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE content=VALUES(content), 
                    comment_nums=VALUES(comment_nums),update_time=VALUES(update_time)
                    """

        create_time = datetime.datetime.fromtimestamp(self["create_time"]).strftime(SQL_DATETIME_FORMAT)
        update_time = datetime.datetime.fromtimestamp(self["update_time"]).strftime(SQL_DATETIME_FORMAT)
        params = (self["zhihu_id"], self["url"], self['question_id'], self["author_id"],
                  self["content"], self["praise_nums"], self["comment_nums"], create_time,
                  update_time, self["crawl_time"].strftime(SQL_DATETIME_FORMAT))

        return insert_sql, params
