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
        raw['url'] = news['wap_url'] 
        raw['stitle'] = news['short_intro']
        raw['cTime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(news['createtime']))
        raw['title'] = news['intro']
        raw['class'] = "图片" 
        raw['image'] = news['img_url']
        print json.dumps(raw, ensure_ascii=False)  

def getimage(news):
    if news['allPics']['total'] == 0:
        return ""

    url = news['allPics']['pics'][0]['imgurl']
    return url 

def urljump(url):
    if url.find('jump') > -1:
        url = re.findall("url=(.+)$", url)[0]
        url = unquote(url)
        
    return url

def dowork():
    page = 1
    while page < 70:
        timestamp = str(int(time.time()))
        url = "http://photo.sina.cn/aj/index?vt=4&wm=&page=" + str(page) + "&cate=recommend&_=" + timestamp + "&callback=jsonp1"
        work(url)
        page += 1
        #break

if __name__ == '__main__':
    dowork()

