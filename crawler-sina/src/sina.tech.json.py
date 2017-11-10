# -*- coding: utf-8 -*-

from urllib import unquote
import re
import requests
import json
import time
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

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

    newslist = data['data']
    for news in newslist:
        raw = {}
        raw['url'] = news['link'] 
        raw['stitle'] = news['wap_title']
        raw['cTime'] = news['date'] 
        raw['title'] = news['title']
        raw['class'] = "科技" 
        if 'img' not in news.keys():
            continue
        raw['image'] = getimage(news['img'])
        print json.dumps(raw, ensure_ascii=False)  

def getimage(url):
    image = url
    param = re.findall('transform(.+)/', url)
    if len(param) > 0:
        image = "http://n.sinaimg.cn/tech/transform" + param[0]

    return image

def dowork():
    page = 1
    while page < 81:
        timestamp = str(int(time.time()))
        url = "https://interface.sina.cn/ent/feed.d.json?ch=tech&col=tech&act=more&t=1489824825378&show_num=10&page=" + str(page) + "&jsoncallback=&_=" + timestamp + "&callback=callback"
        work(url)
        page += 1
        #break

if __name__ == '__main__':
    dowork()

