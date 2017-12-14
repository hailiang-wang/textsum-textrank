#!/usr/bin/env python
# -*- coding: utf-8 -*-
#===============================================================================
#
# Copyright (c) 2017 <> All Rights Reserved
#
#
# File: /Users/hain/ai/textsum-textrank/src/evaluate.py
# Author: Hai Liang Wang
# Date: 2017-11-06:16:24:43
#
#===============================================================================

"""
   
"""
from __future__ import print_function
from __future__ import division

__copyright__ = "Copyright (c) 2017 . All Rights Reserved"
__author__    = "Hai Liang Wang"
__date__      = "2017-11-06:16:24:43"


import os
import sys
curdir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(curdir)

if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding("utf-8")
    # raise "Must be using Python 3"

import unittest
import data_processor
import json
import summarizer
from tqdm import tqdm

sz = summarizer.Summarizer()

def append_line(file, line):
    '''
    append a line to file
    '''
    with open(file, "a") as fout:
        fout.write(line)

# run testcase: python /Users/hain/ai/textsum-textrank/src/evaluate.py Test.testExample
class Test(unittest.TestCase):
    '''
    
    '''
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_testcase_id_tokenlize(self):
        from_ = os.path.join(curdir, os.path.pardir, "tmp", "testcase.id.txt")
        to_ = os.path.join(curdir, os.path.pardir, "tmp", "testcase.id.tokens")
        if os.path.exists(to_): os.remove(to_)
        with open(from_, "r") as fin, open(to_, "w") as fout:
            for x in fin.readlines():
                o = x.split("\t")
                if len(o) == 2:
                    msg_id, content = [y.strip() for y in o]
                    j = json.loads(content)
                    z = [msg_id]
                    for y_, y in sz.tokenlize(j['content'], j['title'], punct = False, stopword = False):
                        z.append('%s\001%s' % (y_, y))
                    append_line(to_, "\t".join(z) + "\n")

    def test_testcase_id_ranking(self):
        from_ = os.path.join(curdir, os.path.pardir, "tmp", "testcase.id.txt")
        to_ = os.path.join(curdir, os.path.pardir, "tmp", "testcase.id.ranking")
        if os.path.exists(to_): os.remove(to_)
        with open(from_, "r") as fin, open(to_, "w") as fout:
            for x in fin.readlines():
                o = x.split("\t")
                if len(o) == 2:
                    msg_id, content = [y.strip() for y in o]
                    j = json.loads(content)
                    r = sz.ranking(title = j['title'], content = j['content'])
                    if len(r) > 0:
                        r = [str(p) for p in r]
                        fout.write("%s\t%s\n" % (msg_id, "\t".join(r)))


    def test_news_json_tokenlize(self):
        from_ = os.path.join(curdir, os.path.pardir, "tmp", "news.json.keyword")
        to_ = os.path.join(curdir, os.path.pardir, "tmp", "news.json.sen.tokens")
        if os.path.exists(to_): os.remove(to_)
        with open(from_, "r") as fin, open(to_, "w") as fout:
            for x in fin.readlines():
                o = x.split("\t")
                if len(o) == 2:
                    msg_id, content = [y.strip() for y in o]
                    j = json.loads(content)
                    z = [msg_id]
                    for y_, y in sz.tokenlize(j['content'], j['title'], punct = False, stopword = False):
                        z.append('%s\001%s' % (y_, y))
                    append_line(to_, "\t".join(z) + "\n")

    def test_ranking_keywords_data(self):
        from_ = os.path.join(curdir, os.path.pardir, "tmp", "news.json.keyword")
        to_ = os.path.join(curdir, os.path.pardir, "tmp", "news.json.sen.ranking")
        if os.path.exists(to_): os.remove(to_)
        with open(from_, "r") as fin, open(to_, "w") as fout:
            for x in fin.readlines():
                o = x.split("\t")
                if len(o) == 2:
                    msg_id, content = [y.strip() for y in o]
                    j = json.loads(content)
                    r = sz.ranking(title = j['title'], content = j['content'])
                    if len(r) > 0:
                        r = [str(p) for p in r]
                        fout.write("%s\t%s\n" % (msg_id, "\t".join(r)))

    def test_evaluate_gf_data(self):
        print("test_evaluate_gf_data")
        f_from = os.path.join(curdir, "resources", "info500.json")
        f_to = os.path.join(curdir, os.path.pardir, "tmp", "text_rank_evaluate.json")
        f_trace = os.path.join(curdir, os.path.pardir, "tmp", "evaluate.trace")
        if os.path.exists(f_to): os.remove(f_to)
        if os.path.exists(f_trace): os.remove(f_trace)
        output = []
        with open(f_from, "r") as fin:
            for x in tqdm(fin.readlines()):
                o = json.loads(x.strip())
                content = o["content"]
                title = o["title"]
                abstract = sz.extract(content = content, title = title, title_weight = 0.4, rate = 140)
                keywords, _ = sz.keywords(content)
                if abstract:
                    output.append({
                                  "content": content,
                                  "headline": title,
                                  "predict": abstract,
                                  "_id": o["_id"],
                                  "uuid": o["uuid"],
                                  "keywords": keywords,
                                  "rank": []
                                  # "rank": "<br><br>".join(["score: %s| %s" % (b ,a) for (a, b) in zip(abstract, scores)])
                                  })
                    tokens = sz.tokenlize(content)
                    # print("scores[0]:", scores[0])
                    # print("abstract[0]:", abstract[0])
                    # print("tokens:", tokens)
            
        with open(f_to, "w") as fout:
            fout.write(json.dumps(output, ensure_ascii=False))


def test():
    unittest.main()

if __name__ == '__main__':
    test()
