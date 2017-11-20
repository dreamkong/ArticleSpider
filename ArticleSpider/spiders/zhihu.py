# -*- coding: utf-8 -*-
import scrapy
import re
import json
import requests


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com/']

    headers = {
        "HOST": "www.zhihu.com",
        "Referer": "https://www.zhizhu.com",
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0"
    }

    def parse(self, response):
        pass

    def start_requests(self):
        return [scrapy.Request('https://www.zhihu.com/#signin', headers=self.headers, callback=self.login)]

    def get_captcha():
        import time
        t = str(int(time.time() * 1000))
        captcha_url = "https://www.zhihu.com/captcha.gif?r={0}&type=login".format(t)
        t = session.get(captcha_url, headers=headers)
        with open("captcha.jpg", "wb") as f:
            f.write(t.content)
            f.close()

        from PIL import Image
        try:
            im = Image.open('captcha.jpg')
            im.show()
            im.close()
        except:
            pass

        captcha = input("输入验证码\n>")
        return captcha

    def login(self, response):

        response_text = response.text
        xsrf = ''
        match_obj = re.match('.*name="_xsrf" value="(.*?)"', response_text, re.DOTALL)
        if match_obj:
            xsrf = match_obj.group(1)

        if xsrf:
            post_url = "https://www.zhihu.com/login/email"
            post_data = {
                "_xsrf": xsrf,
                "email": '48486297@qq.com',
                "password": '521211',
                # "captcha": get_captcha()
            }
            return [scrapy.FormRequest(
                url=post_url,
                formdata=post_data,
                headers=self.headers,
                callback=self.check_login
            )]

    def check_login(self, response):
        # 检查服务器的返回数据是是否成功
        text_json = json.loads(response.text)
        if "msg" in text_json and text_json["msg"] == "登录成功":
            for url in self.start_urls:
                yield scrapy.Request(url, dont_filter=True, headers=self.headers)
