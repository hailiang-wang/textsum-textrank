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

if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding("utf-8")
    # raise "Must be using Python 3"

import unittest
import json
from BeautifulSoup import BeautifulSoup
from common import html_download

hd = html_download.HtmlDownload()

def parse_json_list(from_, to_):
    '''
    crawl links for title and content
    '''
    with open(from_, "r") as fin:
        for x in fin.readlines():
            o = json.loads(x)
            print(o["title"], o["url"])
            code, html = hd.GetHtml(o["url"], None, None, True)
            doc = BeautifulSoup(html, fromEncoding=code)
            desc = doc.find('meta', attrs={"name": "description"})
            print("description:", desc)
            
            break

# run testcase: python /Users/hain/ai/textsum-textrank/crawler-sina/src/sina.finance.parse.py Test.testExample
class Test(unittest.TestCase):
    '''
    
    '''
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_parse_json_list(self):
        f_in=os.path.join(curdir, os.path.pardir, "data", "2017-11-06-13-29.sina.news.utf8.json.txt")
        f_out=os.path.join(f_in, ".parsed")
        parse_json_list(f_in, f_out)

def test():
    unittest.main()

if __name__ == '__main__':
    test()
