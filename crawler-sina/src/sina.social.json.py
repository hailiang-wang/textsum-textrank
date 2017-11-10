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

    newslist = data['result']['data']['list']
    for news in newslist:
        raw = {}
        raw['url'] = urljump(news['URL'])
        raw['stitle'] = news['stitle']
        raw['cTime'] = news['cdateTime']
        raw['title'] = news['title']
        raw['class'] = "社会" 
        raw['image'] = getimage(news)
        print json.dumps(raw, ensure_ascii=False)  

def getimage(news):
    if news['allPics']['total'] == 0:
        return ""

    url = news['allPics']['pics'][0]['imgurl']
    url = url.replace("http://k.sinaimg.cn/n", "http://n.sinaimg.cn")
   
    if url.find("n.sinaimg.cn") > -1:
        url = re.findall("^(.+)/", url)[0]

    return url 

def urljump(url):
    if url.find('jump') > -1:
        url = re.findall("url=(.+)$", url)[0]
        url = unquote(url)
        
    return url

def dowork():
    page = 1
    while page < 34:
        timestamp = str(int(time.time()))
        url = "http://interface.sina.cn/wap_api/layout_col.d.json?showcid=37766&col=37766&level=1%2C2&show_num=30&page=" + str(page) + "&act=more&jsoncallback=&_=" + timestamp + "&callback=jsonp1"
        work(url)
        page += 1
        #break

if __name__ == '__main__':
    dowork()

