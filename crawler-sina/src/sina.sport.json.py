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
        raw['class'] = "体育" 
        raw['image'] = ""
        if 'img' in news.keys():
            raw['image'] = getimage(news['img'])
        print json.dumps(raw, ensure_ascii=False)  

def getimage(url):
    image = "" 
    param = re.findall('transform(.+)/', url)
    if len(param) > 0:
        image = "http://n.sinaimg.cn/sports/transform" + param[0]

    if image == "":
        param = re.findall('translate(.+)/', url)
        if len(param) > 0:
            image = "http://n.sinaimg.cn/translate" + param[0]

    if image == "":
        param = re.findall('sinacn(.+)/', url)
        if len(param) > 0:
            image = "http://n.sinaimg.cn/sinacn" + param[0]

    if image == "":
        return url

    return image

def dowork():
    page = 1
    while page < 80:
        timestamp = str(int(time.time()))
        url = "https://interface.sina.cn/ent/feed.d.json?ch=sports&col=sports&act=more&t=" + timestamp + "&show_num=10&page=" + str(page) + "&jsoncallback=&_=" + timestamp + "&callback=callback"
        work(url)
        page += 1
        #break

if __name__ == '__main__':
    dowork()

