#!/usr/bin/env python
# -*- coding: utf-8 -*-
#===============================================================================
#
# Copyright (c) 2017 <> All Rights Reserved
#
#
# File: /Users/hain/ai/textsum-textrank/crawler-sina/src/sina.finance.parse.py
# Author: Hai Liang Wang
# Date: 2017-11-06:13:57:35
#
#===============================================================================

"""
   
"""
from __future__ import print_function
from __future__ import division

__copyright__ = "Copyright (c) 2017 . All Rights Reserved"
__author__    = "Hai Liang Wang"
__date__      = "2017-11-06:13:57:35"


import os
import sys
curdir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(curdir)

# if sys.version_info[0] < 3:
#     reload(sys)
#     sys.setdefaultencoding("utf-8")
#     # raise "Must be using Python 3"

import urllib2
import chardet
import cookielib
import traceback
import urllib
import random

g_headers = {
    'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
}

g_cookie_file = "cookie.txt"
g_default_header = [
    ('User-Agent','Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2853.0 Safari/537.36')
]
# ('Referer','http://www.newworld-china.com/index.php/gallery-105.html')

class HtmlDownload:
    def __init__(self):
        # cookie = cookielib.CookieJar()
        self.cookie = cookielib.MozillaCookieJar(g_cookie_file)
        self.handler = urllib2.HTTPCookieProcessor(self.cookie)
        self.opener = urllib2.build_opener(self.handler)
        self.opener.addheaders = g_default_header
        # self.opener.addheaders.append(g_headers)

    def GetHtml(self, url, data = None, header = None, is_bin=False):
        '''
        :param url:
        :return: encode, html
        '''
        try:
            if data:
                data = urllib.urlencode(data)
            if header:
                self.opener.addheaders = g_default_header + header
            response = self.opener.open(url, data)
            html = response.read()
            if is_bin:
                return None, html
            # req = urllib2.Request(url, headers=g_headers)
            # response = urllib2.urlopen(req)
            # html = response.read()
        except:
            print(url)
            print(traceback.format_exc())
            return None, None
        return self.GetEncode(html)

    def GetEncode(self, html):
        try:
            html.decode("utf8")
            return "utf8", html
        except:
            pass
        try:
            html.decode("gbk")
            return "gbk", html
        except:
            pass
        try:
            html.decode('gb2312')
            return "gb2312", html
        except:
            pass

        chardit1 = chardet.detect(html)
        if chardit1["encoding"] == None:
            return None, None
        html = html.decode('utf8', 'ignore').encode('utf-8')
        return "utf8", html

import unittest

# run testcase: python /Users/hain/ai/textsum-textrank/crawler-sina/src/sina.finance.parse.py Test.testExample
class Test(unittest.TestCase):
    '''
    
    '''
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_download(self):
        ht = HtmlDownload()
        with open("/tmp/finance.sina.com.cn.html", "wb") as fw:
            en, html = ht.GetHtml("http://finance.sina.com.cn/fund/", None, None, True)
            fw.write(html)

def test():
    unittest.main()

if __name__ == '__main__':
    test()