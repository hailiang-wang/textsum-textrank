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
        raw['url'] = news['url'] 
        if 'stitle' in news:
            raw['stitle'] = news['stitle']
        if 'cTime' in news:
            raw['cTime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(news['ctime']))
        if not 'title' in news: continue
        raw['title'] = news['title']
        raw['class'] = "财经" 
        raw['image'] = news['thumb']
        print json.dumps(raw, ensure_ascii=False)  

def dowork():
    page = 1
    while page < 31:
        timestamp = str(int(time.time()))
        url = "http://cre.dp.sina.cn/api/v3/get?callback=&cateid=y&cre=tianyi&mod=wfin&merge=3&statics=1&impress_id=null%2C689031a7d4333b969b97d2741c1eae9e%2Cae0a264f9345339c90a9458ff33c5229%2C5a5158a9b5a73840a236fa500cfb7ede%2Cb25d853335ee34feb91f6f19d2111673%2C392fc451f82632edbae0e29ed4e9cd97%2C5e5df4457cb3375ca3030778975acd6e%2Cd7d272f207713be7b9368e2fc00b7e0e%2C84aed2a06be83d47bdaf3ed5649b9895%2Cc590f2b2b92e375795a7ffa2c05544ba%2C2eafe830c0f33f98a6bba2942e7ee8c7%2C1e974352a3733ad4a232fce80d084894%2Cb1c1b8544e563e27a007889f26c924af%2C4065c5db52bb362eaac838461d6e9f19%2C3790ae36fb783011b0d608c4218d203d%2Cb49b341dffd93089a78711d6f0fde5bd%2C95769fa461f93dbfb6b544fbc07ea682%2Cde05acca91c93be0a37e5059c5b03d9c%2C7ade5d369def3713a0d43a14093d7adf%2C2f526644f6b132c4a553212a94d6b8ff%2C42d016867e7a38fcb3d1deb620709aad&action=1&up=" + str(page) + "&down=0&tm=" + timestamp + "&_=1489823749265"
        work(url)
        page += 1
        #break

if __name__ == '__main__':
    dowork()

