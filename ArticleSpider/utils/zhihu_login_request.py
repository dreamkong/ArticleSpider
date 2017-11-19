# _*_ coding:utf-8 _*_
__author__ = 'dreamkong'

import requests

try:
    # py2
    import cookielib
except:
    # py3
    import http.cookiejar as cookielib

import re

session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename='cookie.txt')
# try:
#     session.cookies.

agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
headers = {
    'HOST': 'www.zhihu.com',
    'Referer': 'https://www.zhihu.com',
    'User-Agent': agent
}


def get_xsrf():
    # 获取xsrf
    response = session.get('https://www.zhihu.com', headers=headers)
    text = '<input type="hidden" name="_xsrf" value="2abbc22938b648fd5bcc8ed1ec5633a6"/>'
    match_obj = re.match('.*name="_xsrf" value="(.*?)"', response.text)
    if match_obj:
        print(match_obj.group(1))
        return match_obj.group(1)
    return ''


def get_index():
    response = session.get()


def zhihu_login(account, password):
    # 知乎登录
    if re.match('^1\d{10}', account):
        print('手机号码登录')
        post_url = 'https://www.zhihu.com/login/phone_num'
    else:
        print('邮箱登录')
        post_url = 'https://www.zhihu.com/login/email'
    post_data = {
        '_xsrf': get_xsrf,
        'phone_num': account,
        'password': password,
    }

    response_text = session.post(post_url, data=post_data, headers=headers)
    session.cookies.save()


zhihu_login('48486297@qq.com', '521211')
{
    "r": 1,
    "errcode": 100030,

    "data": {"account": "\u767b\u5f55\u8fc7\u4e8e\u9891\u7e41\uff0c\u8bf7\u7a0d\u540e\u91cd\u8bd5"},

    "msg": "\u767b\u5f55\u8fc7\u4e8e\u9891\u7e41\uff0c\u8bf7\u7a0d\u540e\u91cd\u8bd5"

}