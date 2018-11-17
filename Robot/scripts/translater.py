# -*- coding: utf-8 -*-
from re import compile
from requests import get
from md5 import md5

TRANSLATER_ADDR = u"http://api.fanyi.baidu.com/api/trans/vip/translate"
JSON = {u'from': u'auto',
        u'to': u'auto',
        u'appid': '20180822000197576',
        u'salt': '3'}
        
zhPattern = compile(u'[\u4e00-\u9fa5]+')

def check_language(text):
    if zhPattern.search(text):
        return 1
    return 2

def translate(text):
    try:
        JSON[u'q'] = text.encode('utf-8')
    except:
        return text
    string = JSON[u'appid'] + JSON[u'q'] + JSON[u'salt'] + '5Ag7XogguSMXVF7tQKfr'
    JSON[u'sign'] = md5(string).hexdigest()
    res = get(TRANSLATER_ADDR, JSON).json()
    return res[u'trans_result'][0][u'dst'].encode(u'utf-8')

if __name__ == '__main__':

    while True:
        print translate(input(u'What you want to say?'))
