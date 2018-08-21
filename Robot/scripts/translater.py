# -*- coding: utf-8 -*-
from re import compile
from requests import post

TRANSLATER_ADDR = "http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule"
JSON = {"from": "AUTO",
        "to": "AUTO",
        "smartresult": "dict",
        "client": "fanyideskweb",
        "doctype": "json",
        "version": "2.1",
        "keyfrom": "fanyi.web",
        "action": "FY_BY_REALTIME",
        "typoResult": "true"}
zhPattern = compile(u'[\u4e00-\u9fa5]+')

def check_language(text):
    if zhPattern.search(text[4:]):
        return 1
    return 2

def translate(text):
    JSON['i'] = text
    res = post(TRANSLATER_ADDR, data=JSON).json()
    return res['translateResult'][0][0]['tgt']

if __name__ == '__main__':

    while True:
        print translate(input('What you want to say?'))
