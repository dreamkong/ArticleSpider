# _*_ coding:utf-8 _*_

import hashlib

import re


def get_md5(url):
    if isinstance(url, str):
        url = url.encode('utf-8')
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


def extract_nums(value):
    match_re = re.match('.*(\d).*', value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0
    return nums


if __name__ == '__main__':
    print(get_md5('http://jobble.com'.encode('utf-8')))
