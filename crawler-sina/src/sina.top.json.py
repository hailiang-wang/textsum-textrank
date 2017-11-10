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
        raw['class'] = "排行" 
        raw['image'] = ""
        if 'img' in news.keys():
            raw['image'] = getimage(news['img'])
        print json.dumps(raw, ensure_ascii=False)  

def getimage(url):
    url = url.replace("http://k.sinaimg.cn/n", "http://n.sinaimg.cn")
    if url.find("n.sinaimg.cn") > -1:
        url = re.findall("^(.+)/", url)[0]

    return url 

def dowork():
    page = 1
    while page < 81:
        timestamp = str(int(time.time()))
        url = "https://interface.sina.cn/ent/feed.d.json?ch=news&col=news&act=more&t=" + timestamp + "&show_num=10&page=" + str(page) + "&jsoncallback=&_=" + timestamp + "&callback=callback"
        work(url)
        page += 1
        #break

if __name__ == '__main__':
    dowork()

