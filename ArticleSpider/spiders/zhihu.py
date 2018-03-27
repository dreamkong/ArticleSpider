# -*- coding: utf-8 -*-
import datetime
import re
import json
from urllib import parse

import requests
import scrapy
from ArticleSpider.utils import config
from scrapy.loader import ItemLoader
from ArticleSpider.items import ZhihuQuestionItem, ZhihuAnswerItem

session = requests.session()


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com/']

    start_answer_url = 'https://www.zhihu.com/api/v4/questions/{0}/answers?include=data%5B%2A%5D.' \
                       'is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_' \
                       'action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest' \
                       '_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_' \
                       'count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview' \
                       '_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_' \
                       'author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cupvoted_followees%3Bdata%5B%2A%5D.mark_' \
                       'infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%3F%28type%3Dbest_' \
                       'answerer%29%5D.topics&limit={1}&offset={2}&sort_by=default'

    agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) ' \
            'Chrome/61.0.3163.100 Safari/537.36'
    headers = {
        'HOST': 'www.zhihu.com',
        'Referer': 'https://www.zhihu.com',
        'User-Agent': agent
    }

    custom_settings = {
        "COOKIES_ENABLED": True
    }

    def parse(self, response):
        all_urls = response.css("a::attr(href)").extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda x: True if x.startswith('https') else False, all_urls)
        for url in all_urls:
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", url)
            if match_obj:
                # 如果提取到question相关页面则下载并进一步处理
                requests_url = match_obj.group(1)
                yield scrapy.Request(url=requests_url, headers=self.headers, callback=self.parse_question)
            else:
                # 如果不是question页面则直接进一步跟踪
                yield scrapy.Request(url=url, headers=self.headers, callback=self.parse)

    def parse_question(self, response):
        # 处理question界面
        global question_id
        match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", response.url)
        if match_obj:
            question_id = int(match_obj.group(2))

        item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)

        if 'QuestionHeader-title' in response.text:
            # 处理新版本
            item_loader.add_value('zhihu_id', question_id)
            item_loader.add_css('topics', '.QuestionHeader-topics .Popover div::text')
            item_loader.add_value('url', response.url)
            item_loader.add_css('title', 'h1.QuestionHeader-title::text')
            item_loader.add_css('content', '.QuestionHeader-detail .RichText span::text')
            item_loader.add_css('answer_nums', '.List-header > h4 > span::text')
            item_loader.add_css('comment_nums', '.QuestionHeader-Comment button::text')
            item_loader.add_css('watch_nums', '.NumberBoard-itemValue::text')
        else:
            # 处理旧版本
            item_loader.add_xpath("title", "//*[@id='zh-question-title']/h2/a/text()"
                                           "|//*[@id='zh-question-title']/h2/span/text()")
            item_loader.add_css("content", "#zh-question-detail")
            item_loader.add_value("url", response.url)
            item_loader.add_value("zhihu_id", question_id)
            item_loader.add_css("answer_num", "#zh-question-answer-num::text")
            item_loader.add_css("comments_num", "#zh-question-meta-wrap a[name='addcomment']::text")
            # item_loader.add_css("watch_user_num", "#zh-question-side-header-wrap::text")
            item_loader.add_xpath("watch_user_num",
                                  "//*[@id='zh-question-side-header-wrap']/text()|"
                                  "//*[@class='zh-question-followers-sidebar']/div/a/strong/text()")
            item_loader.add_css("topics", ".zm-tag-editor-labels a::text")

        question_item = item_loader.load_item()

        yield scrapy.Request(url=self.start_answer_url.format(question_id, 20, 0), headers=self.headers,
                             callback=self.parse_answer)
        yield question_item

    def parse_answer(self, response):
        # 处理question的answer
        ans_json = json.loads(response.text)
        is_end = ans_json["paging"]["is_end"]
        next_url = ans_json["paging"]["next"]

        # 提取answer的具体字段
        for answer in ans_json["data"]:
            answer_item = ZhihuAnswerItem()
            answer_item["zhihu_id"] = answer["id"]
            answer_item["url"] = answer["url"]
            answer_item["question_id"] = answer["question"]["id"]
            answer_item["author_id"] = answer["author"]["id"] if "id" in answer["author"] else None
            answer_item["content"] = answer["content"] if "content" in answer else None
            answer_item["praise_nums"] = answer["voteup_count"]
            answer_item["comment_nums"] = answer["comment_count"]
            answer_item["create_time"] = answer["created_time"]
            answer_item["update_time"] = answer["updated_time"]
            answer_item["crawl_time"] = datetime.datetime.now()

            yield answer_item

        if not is_end:
            yield scrapy.Request(next_url, headers=self.headers, callback=self.parse_answer)

    def start_requests(self):
        return [scrapy.Request('https://www.zhihu.com/signin', headers=self.headers, callback=self.login)]

    def login_after_captcha(self, response):
        with open("captcha.jpg", "wb") as f:
            f.write(response.body)
            f.close()

        from PIL import Image
        try:
            im = Image.open('captcha.jpg')
            im.show()
            im.close()
        except:
            pass

        captcha = input("输入验证码\n>")

        post_data = response.meta.get("post_data", {})
        post_url = "https://www.zhihu.com/login/email"
        post_data["captcha"] = captcha
        return [scrapy.FormRequest(
            url=post_url,
            formdata=post_data,
            headers=self.headers,
            callback=self.check_login
        )]

    def login(self, response):
        # response_text = response.text
        # xsrf = ''
        # match_obj = re.match('.*name="_xsrf" value="(.*?)"', response_text, re.DOTALL)
        # if match_obj:
        #     xsrf = match_obj.group(1)
        # if xsrf:
        # post_url = "https://www.zhihu.com/login/email"
        post_data = {
            # "_xsrf": xsrf,
            "email": config.USER_NAME,
            "password": config.USER_PASSWORD,
            "captcha": '',
        }
        import time
        t = str(int(time.time() * 1000))
        captcha_url = "https://www.zhihu.com/captcha.gif?r={0}&type=login".format(t)
        yield scrapy.Request(captcha_url, headers=self.headers, meta={"post_data": post_data},
                             callback=self.login_after_captcha)

    def check_login(self, response):
        # 检查服务器的返回数据是是否成功
        print(response.text)
        text_json = json.loads(response.text)
        if "msg" in text_json and text_json["msg"] == "登录成功":
            for url in self.start_urls:
                yield scrapy.Request(url, dont_filter=True, headers=self.headers)
