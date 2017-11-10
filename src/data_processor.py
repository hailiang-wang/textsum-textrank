#!/usr/bin/env python
# -*- coding: utf-8 -*-
#===============================================================================
#
# Copyright (c) 2017 <> All Rights Reserved
#
#
# File: /Users/hain/ai/seq2seq-textsum/src/data_processer.py
# Author: Hai Liang Wang
# Date: 2017-10-18:19:33:36
#
#===============================================================================

"""
   
"""
from __future__ import print_function
from __future__ import division

__copyright__ = "Copyright (c) 2017 . All Rights Reserved"
__author__    = "Hai Liang Wang"
__date__      = "2017-10-18:19:33:36"


import os
import sys
curdir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(curdir)

PLT = 2
if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding("utf-8")
    # raise "Must be using Python 3"
else:
    PLT = 3

import unittest
import xml.etree.ElementTree as ET
import re
import requests
import json
from common import utils as common_utils

def resolve_utf8(word):
    if PLT == 2:
        return word.encode("utf8")
    else:
        return word

output_file = os.path.join(curdir, os.path.pardir, "tmp", "full.sohu.com.raw.txt")

def append_line_to_file(line, file_path):
    with open(file_path, "a") as fout:
        fout.write(line)

def parse_xml(raw_string):
    try:
        root = ET.fromstring(raw_string)
        vals = []
        for child in root:
            vals.append(child.text)
        assert len(vals) == 4, "packed values length should be 4"
        [url, docno, contenttitle, content] = vals
        if contenttitle is not None and content is not None:
            append_line_to_file("%s ++$++ %s\n" % (contenttitle, content), output_file)
    except ET.ParseError as err:
        pass

'''
分词
'''
import jieba
import jieba.posseg as tokenizer
COMPANY_DICT_PATH = os.path.join(curdir, "resources", "vocab.company.utf8")
SOUGOU_DICT_PATH = os.path.join(curdir, "resources", "vocab.sougou.utf8")
STOPWORD_DICT_PATH = os.path.join(curdir, "resources", "stopwords.utf8")
jieba.load_userdict(COMPANY_DICT_PATH)
jieba.load_userdict(SOUGOU_DICT_PATH)
jieba_stopwords = set()

def load_stop_words():
    if len(jieba_stopwords) > 0:
        return True
    if not os.path.exists(STOPWORD_DICT_PATH):
        return None
    with open(STOPWORD_DICT_PATH, "r") as fin:
        for x in fin:
            x = x.strip()
            if not x.startswith("#"): jieba_stopwords.add(x)
    print("jieba stopwords loaded, len %d." % len(jieba_stopwords))
    return True
load_stop_words()

def seg_jieba(body):
    '''
    Jieba tokenizer
    '''
    y = tokenizer.cut(common_utils.to_utf8(body["content"]), HMM=True)
    words, tags = [], []
    for o in y:
        w = common_utils.to_utf8(o.word)
        t = o.flag
        if "type" in body and body["type"] == "nostopword":
            if w in jieba_stopwords: continue
        if "punct" in body and body["punct"] == False:
            if t.startswith("x"): continue
        words.append(w)
        tags.append(t)
    assert len(words) == len(tags), "words and tags should be the same length with jieba tokenizer."
    return words, tags

def word_segment(utterance, vendor = "jieba", punct = False, stopword = True):
    '''
    segment words,
    punct: 是否去掉标点符号, True不去掉
    stopword: 是否去掉停用词, True不去掉
    '''
    words, tags = [], []
    try:
        if vendor == "jieba":
            words, tags = seg_jieba({
                                "type": "nostopword" if not stopword else None,
                                "content": utterance,
                                "punct": punct
                                })
        else:
            raise Exception("None tokenizer.")
    except Exception as e:
        print("seg error\n", utterance, e)
    return words, tags

'''
Sense less words for News data
'''
SENSE_LESS_WORD_PATH = os.path.join(curdir, "resources", "less350.txt")
senseless_words = set()
with open(SENSE_LESS_WORD_PATH, "r") as fin:
    [senseless_words.add(x.strip()) for x in fin.readlines()]
assert len(senseless_words) > 0, "senseless words set should not be empty."

def filter_senseless_words(utterance):
    '''
    segmented word list
    '''
    result = []
    for o in utterance:
        if not o in senseless_words: result.append(o)

    return result


'''
load punct
'''
punct = []
with open(os.path.join(curdir, "resources", "punctuation.utf8"), "r") as fin:
    [ punct.append(x.strip()) for x in fin.readlines()]
assert len(punct) > 0, "punct set should not be empty."

def filter_special_punct(utterance):
    '''
    remove special punct
    '''
    for o in punct:
        utterance = utterance.replace(o, " ")
    return utterance

emoji = []
with open(os.path.join(curdir, "resources", "emoji.utf8"), "r") as fin:
    [ emoji.append(x.strip()) for x in fin.readlines()]
assert len(emoji) > 0, "emoji set should not be empty."

def filter_emoji(utterance):
    '''
    remove 【emoji】
    '''
    for o in emoji:
        utterance = utterance.replace(o, "")
    return utterance

def filter_date(utterance):
    '''
    replace date with TAG_DATE
    '''
    utterance = re.sub(u"\d{1,}\s*年\d{1,}\s*月\d{1,}\s*日", "TDATE", utterance)
    utterance = re.sub(u"\d{1,}\s*月\d{1,}\s*日", "TDATE", utterance)
    utterance = re.sub(u"\d{1,}\s*月\d{1,}\s*日", "TDATE", utterance)
    utterance = re.sub(u"\d{2,}\s*年\d{1,}月", "TDATE", utterance)
    utterance = re.sub("\d{4}-\d{1,2}-\d{1,2}", "TDATE", utterance)
    return utterance

def filter_full_to_half(txt):
    '''
    全角转换为半角: http://www.qingpingshan.com/jb/python/118505.html
    return utf8 string
    '''
    n = []
    txt = common_utils.to_unicode(txt)
    for char in txt:
        num = ord(char)
        if num == 0x3000:
            num = 32
        elif 0xFF01 <= num <= 0xFF5E:
            num -= 0xfee0
        num = unichr(num)
        n.append(num)

    result = ''.join(n)
    return common_utils.to_utf8(result)


def filter_eng_to_tag(utterance):
    '''
    TODO 删除全角的英文: 替换为标签TAG_NAME_EN
    由数字、26个英文字母或者下划线组成的字符串
    '''
    utterance = re.sub("[A-Za-z]+", "TENGLISH", utterance)
    return utterance

'''
load names
'''
person_names = []
with open(os.path.join(curdir, "resources", "names.utf8"), "r") as fin:
    [ person_names.append(x.strip()) for x in fin.readlines()]
assert len(person_names) > 0, "person names set should not be empty."

def filter_name(utterance):
    '''
    将人名替换成 TAG_PERSON_NAME
    '''
    result = []
    for o in utterance:
        if not o in person_names:
            result.append(o)
        else:
            result.append("TPERSON")
    return result

def filter_url(utterance):
    '''
    超链接URL：替换为标签TAG_URL
    '''
    # utterance = re.sub("[a-zA-z]+://[^\s]*", "TAG_URL", utterance)
    utterance = re.sub("http[s]?://[^\s]*", "TURL", utterance)
    return utterance

def filter_number(utterance):
    utterance = re.sub("[^a-zA-Z0-9_]+[0-9.]+", " TNUMBER", utterance)
    utterance = re.sub("[0-9.]+", " TNUMBER", utterance)
    return utterance

def join_none_chinese_utterance(utterance):
    '''
    Join not Chinese chars in a list
    '''
    tmp = []
    result = []
    join = False
    size = len(utterance)
    index = 0
    for x in utterance:
        if common_utils.is_zhs(x) or (x in ["TNUMBER", "TPERSON", "TURL", "TDATE"]):
            join = False
            if len(tmp) > 0:
                y = "_".join(tmp)
                result.append(y.upper())
                tmp = []
            result.append(x)
        else:
            join = True
            tmp.append(x)
        index += 1
        if index == size and len(tmp) > 0:
            result.append(tmp)
    return result

def extract_sohu_full_raw_txt():
    data_path = os.path.join(curdir, os.path.pardir, "tmp", "news_sohusite_xml.uft8")
    with open(data_path, "r") as m:
        t = []
        for x in m.readlines():
            x = x.strip()
            if x == "<doc>":
                t = []
                t.append(x)
            elif x == "</doc>":
                t.append(x)
                parse_xml("".join(t))
            else:
                t.append(x)

def extract_sohu_business_raw_txt():
    resource_list = os.path.join(curdir, "resources", "news.data_list.txt")
    root_dir = os.path.join(curdir, os.path.pardir)
    data_xmls = []
    with open(resource_list, "r") as rin:
        [data_xmls.append(os.path.join(root_dir, x).strip()) for x in rin.readlines()]

    for o in data_xmls:
        with open(o, "r") as m:
            t = []
            for x in m.readlines():
                x = x.strip()
                if x == "<doc>":
                    t = []
                    t.append(x)
                elif x == "</doc>":
                    t.append(x)
                    parse_xml("".join(t))
                else:
                    t.append(x)

def solo_tnumber_utterance(utterance):
    '''
    replace multiple TNUMBER with one TNUMBER
    '''
    # print("solo_tnumber_utterance in << ", " ".join(utterance))
    result = []
    pre = None
    for o in utterance:
        o = o.strip()
        if pre == "TNUMBER" and o == "TNUMBER":
            pass
        elif pre == "TNUMBER" and o != "TNUMBER":
            pre = None
            result.append(o)
        elif pre != "TNUMBER" and o == "TNUMBER":
            result.append(o)
            pre = "TNUMBER"
        elif pre != "TNUMBER" and o != "TNUMBER":
            result.append(o)
            pre = None
    return result

def solo_space_utterance(utterance):
    '''
    replace multiple spaces with one space
    '''
    return re.sub(' +',' ', utterance).strip()

def preprocess_gf_data():
    '''
    •   特殊字符：去除特殊字符，如：“「，」,￥,…”；
    •   括号内的内容：如表情符，【嘻嘻】，【哈哈】
    •   日期：替换日期标签为TAG_DATE，如：***年*月*日，****年*月，等等
    •   超链接URL：替换为标签TAG_URL；
    •   删除全角的英文：替换为标签TAG_NAME_EN；
    •   替换数字：TAG_NUMBER；
    '''
    import langid
    file_path = os.path.join(curdir, os.path.pardir, "tmp", "gf_data.csv")
    output_path = os.path.join(curdir, os.path.pardir, "tmp", "gf_data.raw")
    to_content = "%s.content" % output_path
    to_title = "%s.title" % output_path
    if os.path.exists(to_content): os.remove(to_content)
    if os.path.exists(to_title): os.remove(to_title)

    with open(file_path, "r") as fin:
        for x in fin.readlines():
            x = x.split("+++++")
            assert len(x) == 2, "business news should be in 2"
            title = x[0].strip()
            content = x[1].strip()

            lang_t = langid.classify(title)
            lang_c = langid.classify(content)

            if lang_c[0] != "zh" or lang_t[0] != "zh": continue
            
            # filters
            content = filter_full_to_half(content)
            content = filter_date(content)
            content = filter_number(content)
            content = filter_special_punct(content)
            content = filter_emoji(content)
            content = filter_url(content)
            c, _ = word_segment(content)
            c = filter_name(c)

            title = filter_full_to_half(title)
            title = filter_date(title)
            title = filter_number(title)
            title = filter_special_punct(title)
            title = filter_emoji(title)
            title = filter_url(title)
            t, _ = word_segment(title)

            # post word segment
            c = filter_senseless_words(c)
            t = filter_senseless_words(t)
            t = filter_name(t)

            c = solo_tnumber_utterance(solo_space_utterance(" ".join(c))) 
            t = solo_tnumber_utterance(solo_space_utterance(" ".join(t)))

            # write line to files
            if len(c.split(" ")) > 2 and len(t.split(" ")) > 2:
                append_line_to_file(c + "\n", to_content)
                append_line_to_file(t + "\n", to_title)

def sohu_news_remove_senseless_words():
    from_title_file = os.path.join(curdir, os.path.pardir, "tmp", "full.sohu.com.title.txt")
    from_content_file = os.path.join(curdir, os.path.pardir, "tmp", "full.sohu.com.content.txt")
    to_title_file = os.path.join(curdir, os.path.pardir, "tmp", "full.sohu.com.title.v2.txt")
    to_content_file = os.path.join(curdir, os.path.pardir, "tmp", "full.sohu.com.content.v2.txt")

    with open(from_title_file, "r") as fin_t, open(from_content_file, "r") as fin_c:
        for (t, c) in zip(fin_t.readlines(), fin_c.readlines()):
            t = filter_senseless_words(t.split())
            c = filter_senseless_words(c.split())

            if len(t) > 0 and len(c) > 0:
                append_line_to_file(" ".join(c) + "\n", to_content_file)
                append_line_to_file(" ".join(t) + "\n", to_title_file)

def preprocess_sohu_full_raw_txt():
    '''
    •   特殊字符：去除特殊字符，如：“「，」,￥,…”；
    •   括号内的内容：如表情符，【嘻嘻】，【哈哈】
    •   日期：替换日期标签为TAG_DATE，如：***年*月*日，****年*月，等等
    •   超链接URL：替换为标签TAG_URL；
    •   删除全角的英文：替换为标签TAG_NAME_EN；
    •   替换数字：TAG_NUMBER；
    '''
    file_path = os.path.join(curdir, os.path.pardir, "tmp", "full.sohu.com.raw.txt")
    with open(file_path, "r") as fin:
        for x in fin.readlines():
            x = x.split(" ++$++ ")
            assert len(x) == 2, "business news should be in 2"
            title = x[0].strip()
            content = x[1].strip()
            # filters
            content = filter_full_to_half(content)
            content = filter_date(content)
            content = filter_number(content)
            content = filter_special_punct(content)
            content = filter_emoji(content)
            content = filter_url(content)
            c, _ = word_segment(content)
            c = filter_name(c)

            title = filter_full_to_half(title)
            title = filter_date(title)
            title = filter_number(title)
            title = filter_special_punct(title)
            title = filter_emoji(title)
            title = filter_url(title)
            t, _ = word_segment(title)
            t = filter_name(t)

            c = solo_tnumber_utterance(solo_space_utterance(" ".join(c))) 
            t = solo_tnumber_utterance(solo_space_utterance(" ".join(t)))

            # write line to files
            if len(c.split(" ")) > 3 and len(t.split(" ")) > 3:
                append_line_to_file(c + "\n", os.path.join(curdir, os.path.pardir, "tmp", "full.sohu.com.content.txt"))
                append_line_to_file(t + "\n", os.path.join(curdir, os.path.pardir, "tmp", "full.sohu.com.title.txt"))

class Test(unittest.TestCase):
    '''
    
    '''
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_filter_url(self):
        print(filter_url("fp http://www.deepnlp.org/blog/textsum-seq2seq-attention/ 天气不错中"))

    def test_filter_date(self):
        content = "６月２０日：粮油、肉类、禽蛋、奶类价格稳定"
        content = filter_full_to_half(content)
        content = filter_special_punct(content)
        content = filter_emoji(content)
        content = filter_url(content)
        content = filter_date(content)
        content = filter_number(content)  
        print("result:", content)

    def test_filter_number(self):
        content = "G20"
        content = filter_number(content)
        print(content)

    def test_filter_special_punct(self):
        pass

    def test_extract_sohu_business_raw_txt(self):
        extract_sohu_business_raw_txt()

    def test_extract_sohu_full_raw_txt(self):
        extract_sohu_full_raw_txt()

    def test_preprocess_sohu_business_raw_txt(self):
        preprocess_sohu_business_raw_txt()

    def test_preprocess_sohu_full_raw_txt(self):
        preprocess_sohu_full_raw_txt()

    def test_preprocess_gf_data(self):
        preprocess_gf_data()

    def test_sohu_news_remove_senseless_words(self):
        sohu_news_remove_senseless_words()

    def test_solo_tnumber_utterance(self):
        t = "TNUMBER TNUMBER 年 经过 中国 数学 名词 审查 委员会 研究 算学 与 数学 两 词 的 使用 状况 后 确认 以 数学 表示 今天 意义 上 的"
        print(" ".join(solo_tnumber_utterance(t.split()))) 


def test():
    unittest.main()

if __name__ == '__main__':
    test()
