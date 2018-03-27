# _*_ coding:utf-8 _*_
__author__ = 'dreamkong'

import requests
from ArticleSpider.utils import config

try:
    # py2
    import cookielib
except:
    # py3
    import http.cookiejar as cookielib

import re

session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename="cookies.txt")
try:
    session.cookies.load(ignore_discard=True)
except:
    print("cookie未能加载")

agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) ' \
        'Chrome/61.0.3163.100 Safari/537.36'
headers = {
    'HOST': 'www.zhihu.com',
    'Referer': 'https://www.zhihu.com',
    'User-Agent': agent
}


def is_login():
    # 通过个人中心页面返回状态码来判断是否为登录状态
    inbox_url = "https://www.zhihu.com/notifications"
    response = session.get(inbox_url, headers=headers, allow_redirects=False)
    if response.status_code != 200:
        return False
    else:
        return True


def get_xsrf():
    # 获取xsrf
    response = session.get('https://www.zhihu.com', headers=headers)
    text = '<input type="hidden" name="_xsrf" value="2abbc22938b648fd5bcc8ed1ec5633a6"/>'
    print(response.text)
    match_obj = re.match('.*name="_xsrf" value="(.*?)"', response.text)
    if match_obj:
        print(match_obj.group(1))
        return match_obj.group(1)
    return ''


def get_index():
    response = session.get("https://www.zhihu.com", headers=headers)
    with open("index_page.html", "wb") as f:
        f.write(response.text.encode("utf-8"))
    print("ok")


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


def zhihu_login(account, password):
    # 知乎登录
    global post_data, post_url
    if re.match("^1\d{10}", account):
        print("手机号码登录")
        post_url = "https://www.zhihu.com/login/phone_num"
        post_data = {
            "_xsrf": get_xsrf(),
            "phone_num": account,
            "password": password,
            "captcha": get_captcha()
        }
    else:
        if "@" in account:
            # 判断用户名是否为邮箱
            print("邮箱方式登录")
            post_url = "https://www.zhihu.com/login/email"
            post_data = {
                "_xsrf": get_xsrf(),
                "email": account,
                "password": password,
                "captcha": get_captcha()
            }

    response_text = session.post(post_url, data=post_data, headers=headers)
    print(response_text)
    session.cookies.save()


if not is_login():
    zhihu_login(config.USER_NAME, config.USER_PASSWORD)
