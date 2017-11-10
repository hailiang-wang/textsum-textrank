# -*- coding: utf-8 -*-

import requests
import json
import time
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class_list = ['gn', 'gj', 'sh', 'ent', 'mil', 'finance', 'sports', 'tech', 'video']
class_dict = {
    'gn':'国内',
    'gj':'国际',
    'sh':'社会',
    'ent':'娱乐',
    'mil':'军事',
    'finance':'财经',
    'sports':'体育',
    'tech':'科技',
    'video':'视频'
}



# 国内 国际 社会 娱乐 军事 财经 体育 科技 视频

def work(url):
    req = requests.get(url)
    req.encoding = 'utf-8'
    html = req.text
    data = None
    try:
        data = json.loads(html)    
    except Exception, e:
        pass
    
    if data == None:
        return

    newslist = data['result']['data']['list']
    for news in newslist:
        raw = {}
        raw['url'] = news['URL']
        raw['stitle'] = news['stitle']
        raw['cTime'] = news['cTime']
        raw['title'] = news['title']
        raw['class'] = classed(news['URL'])
        raw['image'] = ""
        print json.dumps(raw, ensure_ascii=False)  

def classed(url):
    for v in class_list:
        if url.find(v) > -1:
            return class_dict[v]

    return "其他"

def dowork():
    page = 1
    while page < 34:
        timestamp = str(int(time.time()))
        url = "http://interface.sina.cn/wap_api/news_roll.d.html?col=38790&level=1%2C2&show_num=30&page=" + str(page) + "&act=more&jsoncallback=&_=" + timestamp + "&callback=jsonp1"
        work(url)
        page += 1
        #break

if __name__ == '__main__':
    dowork()

