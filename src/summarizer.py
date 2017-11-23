#!/usr/bin/env python
# -*- coding: utf-8 -*-
#===============================================================================
#
# Copyright (c) 2017 <> All Rights Reserved
#
#
# File: /Users/hain/ai/textsum-textrank/src/summarizer.py
# Author: Hai Liang Wang
# Date: 2017-11-04:14:00:56
#
#===============================================================================

"""
   
"""
from __future__ import print_function
from __future__ import division

__copyright__ = "Copyright (c) 2017 . All Rights Reserved"
__author__    = "Hai Liang Wang"
__date__      = "2017-11-04:14:00:56"


import os
import sys
curdir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(curdir)

if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding("utf-8")
    # raise "Must be using Python 3"
else:
    raise "Must be using Python 2.x"
    sys.exit()

import numpy
import networkx
import itertools
import math
import data_processor
from common import utils as common_utils
from common import log
from common import similarity
from functools import reduce
logger = log.getLogger(__name__)

PUNCT_SENTENCE_ENDS = ["。", "!", "?", "？", "！"]
PUNCT_SENTENCE_EMBED_START = "“" # 断句在嵌套的段落中，比如：他说：“蛇么。”
PUNCT_SENTENCE_EMBED_END = "”"


def normalize(v):
    '''
    normalize array digits to 1
    '''
    norm=numpy.linalg.norm(v, ord=1)
    if norm==0:
        norm=numpy.finfo(v.dtype).eps

    r = v/norm
    return [float("%.5f" % x) for x in r]


class Summarizer():
    '''
    summarize articles
    '''

    def __init__(self):
        pass

    def build_graph(self, nodes):
        """Return a networkx graph instance.
        :param nodes: List of hashables that represent the nodes of a graph.
        """
        gr = networkx.Graph()  # initialize an undirected graph
        gr.add_nodes_from(nodes)
        nodePairs = list(itertools.combinations(nodes, 2))

        # add edges to the graph (weighted by Levenshtein distance)
        for pair in nodePairs:
            firstString = pair[0]
            secondString = pair[1]
            distance = similarity.compare(firstString, secondString, seg=False)
            gr.add_edge(firstString, secondString, weight=distance)

        return gr

    def paragraph_to_sentence(self, paragraph):
        '''
        段落转换为句子
        返回(生成器): 句子
        '''
        status_embed = False
        chars = common_utils.to_utf8(paragraph).decode('utf-8', 'ignore')
        sb = [] # temp sentence buffer
        for x in chars:
            x = x.encode('utf-8', 'ignore')
            if x == PUNCT_SENTENCE_EMBED_START:
                status_embed = True
                sb.append(x)
                continue

            if x == PUNCT_SENTENCE_EMBED_END:
                status_embed = False

            if x in PUNCT_SENTENCE_ENDS and not status_embed:
                sb.append(x)
                yield "".join(sb), x
                sb = []
            else:
                sb.append(x)
        if len(sb) > 0:
            yield "".join(sb), None

        # # print("paragraph: %s \n" % paragraph)
        # w, t = data_processor.word_segment(paragraph, vendor = "jieba", punct = True)
        # sb = [] # temp sentence buffer
        # for x,y in zip(w, t):
        #     if x == PUNCT_SENTENCE_EMBED_START:
        #         status_embed = True
        #         sb.append(x)
        #         continue

        #     if x == PUNCT_SENTENCE_EMBED_END:
        #         status_embed = False

        #     if x in PUNCT_SENTENCE_ENDS and not status_embed:
        #         yield "".join(sb), x
        #         sb = []
        #     else:
        #         sb.append(x)
        # # 当一个段落的结尾没有标点的时候。
        # if len(sb) > 3: yield "".join(sb), None

    def doc_to_paragraphs(self, content):
        '''
        文档转换为段落
        '''
        result = []
        paragraphs = content.split("\n")
        for x in paragraphs:
            x = x.strip()
            is_sentence = False
            # 判断是不是句子，如果不是句子
            # 也许是段落的标题，那么这个句子虽然不能输出，但是包含的词汇权重应该比较大
            # TODO 利用段落标题和headline，这些属于 textteaser 的部分。 
            for o in PUNCT_SENTENCE_ENDS:
                if x.endswith(o):
                    is_sentence = True
                    break
            if is_sentence and len(x) > 0: result.append(x)
        return result

    def doc_to_sentences(self, content):
        '''
        将文档转化为独立的句子
        '''
        result = []
        paragraphs = self.doc_to_paragraphs(content)
        for x in paragraphs:
            for s,p in self.paragraph_to_sentence(x):
                result.append(s)
        return result

    def get_sentence_tokens(self, sentences):
        '''
        生成文章句子list的token list
        '''
        for x in sentences:
            # 去掉标点和停用词
            w, t = data_processor.word_segment(x, vendor = "jieba", punct = False, stopword = False)
            yield " ".join(w)


    def keywords(self, content, title = None, vendor = "tfidf"):
        '''
        抽取方式取文章的关键字
        content: 正文
        title: 标题
        '''
        # 全角转半角
        content = data_processor.filter_full_to_half(content)
        title = data_processor.filter_full_to_half(title) if title else ""
        return data_processor.extract_keywords(content, vendor = vendor)

    def tokenlize(self, content, title = None):
        '''
        Get all tokens as a list for content
        '''
        # 全角转半角
        content = data_processor.filter_full_to_half(content)
        title = data_processor.filter_full_to_half(title) if title else ""
        sentences = self.doc_to_sentences(content)
        # for x in sentences:
        #     print(x)
        #     print("*"*20 + "\n")
        tokens = []

        for x in sentences:
            w, _ = data_processor.word_segment(x, vendor = "jieba", punct = False, stopword = False)
            if len(w) > 3:
                for o in w: tokens.append(o)
        return tokens

    def ranking(self, content, title, title_weight = 0.4):
        '''
        输出句子的排名
        @param     content: 正文
        @param     title: 标题
        @param     title_weight: 标题boost句子的系数
        @param     rate: 摘要的最长长度。如果 rate 大于1，则认为传入固定值，e.g 140;如果 rate 小于1，则认为生成原文的百分比
        @return    list, 句子排名
        '''
        # 全角转半角
        content = data_processor.filter_full_to_half(content)
        title = data_processor.filter_full_to_half(title) if title else ""
        # TODO return sub-title
        sentences = self.doc_to_sentences(content)
        # for x in sentences:
        #     print(x)
        #     print("*"*20 + "\n")
        s2t = dict() # sentence to tokens
        t2s = dict() # tokens to sentence
        t2seq = dict() # tokens to sequence
        t2len = dict() # tokens to length
        tokens = [] # ["word1 word2 word3", ...]
        tt = 0 # token total

        for x_,x in enumerate(sentences):
            w, _ = data_processor.word_segment(x, vendor = "jieba", punct = False, stopword = False)
            if len(w) > 3:
                tt += len(w)
                o = " ".join(w)
                s2t[x] = o
                t2s[o] = x
                t2seq[o] = x_
                t2len[o] = len(common_utils.to_utf8(x).decode("utf8"))
                tokens.append(o)

        '''
        Recall: sort and ranking with textrank
        '''
        graph = self.build_graph(tokens)
        # textrank results
        tr = networkx.pagerank(graph, weight='weight')

        # most important sentences in ascending order of importance
        sort = sorted(tr, key=tr.get,
                       reverse=True)

        sort_tokens, sort_scores = [x for x in sort], [tr[x] for x in sort]
        '''
        Evaluate: re-ranking model with title
        '''
        if title:
            # title tokens and tags
            title_words, _ = data_processor.word_segment(title, vendor = "jieba", punct = False, stopword = False)
            title_sort = [similarity.compare(" ".join(title_words), x, seg = False) for x in sort]
            if len(title_sort) > 0:
                title_sort = normalize(title_sort)
                # title score weighted
                title_sort = [ a*title_weight*(1/len(sort))*100 + b for (a, b) in zip(title_sort, [tr[x] for x in sort])]
                # print("title score: %s" % tsw)
                resort = []
                for (x,y) in zip([ x for _,x in sorted(zip(title_sort, sort), reverse=True)], sorted(title_sort, reverse=True)):
                    # print("text:%s |score: %f" % (x,y))
                    resort.append(x)
                sort = resort

        return [t2seq[x] for x in sort]

    def extract(self, content, title = None, title_weight = 0.4, rate = 0.3):
        '''
        采用抽取方式提取摘要
        @param     content: 正文
        @param     title: 标题
        @param     title_weight: 标题boost句子的系数
        @param     rate: 摘要的最长长度。如果 rate 大于1，则认为传入固定值，e.g 140;如果 rate 小于1，则认为生成原文的百分比
        @return    string: 文本摘要
        '''
        # 全角转半角
        content = data_processor.filter_full_to_half(content)
        title = data_processor.filter_full_to_half(title) if title else ""
        # TODO return sub-title
        sentences = self.doc_to_sentences(content)
        # for x in sentences:
        #     print(x)
        #     print("*"*20 + "\n")
        s2t = dict() # sentence to tokens
        t2s = dict() # tokens to sentence
        t2seq = dict() # tokens to sequence
        t2len = dict() # tokens to length
        tokens = [] # ["word1 word2 word3", ...]
        tt = 0 # token total

        for x_,x in enumerate(sentences):
            w, _ = data_processor.word_segment(x, vendor = "jieba", punct = False, stopword = False)
            if len(w) > 3:
                tt += len(w)
                o = " ".join(w)
                s2t[x] = o
                t2s[o] = x
                t2seq[o] = x_
                t2len[o] = len(common_utils.to_utf8(x).decode("utf8"))
                tokens.append(o)

        '''
        摘要文本的长度
        '''
        max_length = rate
        if rate < 1:
            max_length = math.floor(tt * rate)

        '''
        Recall: sort and ranking with textrank
        '''
        graph = self.build_graph(tokens)
        # textrank results
        tr = networkx.pagerank(graph, weight='weight')

        # most important sentences in ascending order of importance
        sort = sorted(tr, key=tr.get,
                       reverse=True)

        sort_tokens, sort_scores = [x for x in sort], [tr[x] for x in sort]
        '''
        Evaluate: re-ranking model with title
        '''
        if title:
            # title tokens and tags
            title_words, _ = data_processor.word_segment(title, vendor = "jieba", punct = False, stopword = False)
            title_sort = [similarity.compare(" ".join(title_words), x, seg = False) for x in sort]
            if len(title_sort) > 0:
                title_sort = normalize(title_sort)
                # title score weighted
                title_sort = [ a*title_weight*(1/len(sort))*100 + b for (a, b) in zip(title_sort, [tr[x] for x in sort])]
                # print("title score: %s" % tsw)
                resort = []
                for (x,y) in zip([ x for _,x in sorted(zip(title_sort, sort), reverse=True)], sorted(title_sort, reverse=True)):
                    # print("text:%s |score: %f" % (x,y))
                    resort.append(x)
                sort = resort

        # for x in sort: print("sen: %s, score: %f" % (x, tr[x]))
        # normalize([tr[x] for x in sort])
        patch_length = []
        patch_total = 0
        for x in sort:
            patch_total += t2len[x]
            patch_length.append(patch_total)

        extracted = []
        for x_,x in enumerate(patch_length):
            extracted.append(sort_tokens[x_])
            if x > max_length: break

        extracted.sort(key=lambda x: t2seq[x])

        extracted_text = [t2s[x] for x in extracted]

        return "".join(extracted_text)

import unittest

# run testcase: python /Users/hain/ai/textsum-textrank/src/summarizer.py Test.testExample
class Test(unittest.TestCase):
    '''
    
    '''
    def setUp(self):
        self.title = "360回归:交易结构暗藏巧思 投资人有望获丰厚回报"
        self.content = """360借壳方案出炉，为中概股回归之路点亮了一盏灯。如果交易顺利，三六零科技股份有限公司（简称“三六零”）将是中国前几大互联网巨头中唯一一家登陆A股的公司。与近些年的重磅借壳方案相比，三六零504亿元资产规模，远超分众传媒（457亿借壳）、顺丰控股（433亿借壳）、巨人网络（130亿借壳）等的交易规模。
800多页的重组方案，更多精彩藏于细节：低位停牌的江南嘉捷，目前总市值仅有35亿元，悬殊的差距令壳公司原股东权益被大量稀释，虽然在三六零面前壳公司的议价能力微弱，但是交易仍对原实际控制人作了一定的利益补偿安排。同时，三六零的“生意经”首次在A股详细披露，A股投资人的回报空间或将十分丰厚。
交易结构暗藏巧思
504亿元的交易规模，不设配套融资，结构不算复杂，但在该交易中，一笔“9.71%嘉捷机电”的小股权令人关注。
根据证监会2017年1月修改的《上市公司重大资产重组管理办法》，为进一步遏制重组上市（即借壳）的套利空间，取消了重组上市的配套融资，这被视为众多修改的限制条件中最有杀伤力一条。本次三六零的借壳方案中未见配套融资的安排，可谓顺理成章。
交易结构虽然不算复杂，但仍有巧思蕴含其中。方案在出售资产部分中有这样的设计：江南嘉捷拟将除全资子公司嘉捷机电100%股权之外的全部资产、负债、业务、人员、合同、资质及其他一切权利与义务划转至嘉捷机电。在此基础上，江南嘉捷将嘉捷机电90.29%股权以现金方式转让给原控股股东金志峰、金祖铭或其指定的第三方，交易作价16.9亿元；将嘉捷机电另9.71%股权与三六零全体股东拥有的三六零100%股权的等值部分进行置换，此后再由三六零全体股东将这9.71%股权转让给金志峰、金祖铭或其指定的第三方。
仅9.71%的嘉捷机电小股权，为何成为交易中被反复买卖的资产？有投行人士对记者表示，目前借壳经典的操作方式是：资产置换+定向增发+回购资产，即壳公司先将全部原资产与借壳方拟置入资产中等额部分做资产置换，差额部分以新发行的壳公司股份支付；之后壳公司原股东以置出资产账面净值为基础，以现金或股权形式，向新股东回购原置出资产，使公司成为净壳，该部分资产一买一卖间的差价，基本就是对壳公司原股东的补偿。从本方案来看，“嘉捷机电9.71%股权”就是这一重要的调节器。
会计处理堪称“清流”
若交易顺利完成，对投资者来说更为重要的，应是三六零的“生意经”。这家网络安全巨头的业绩和持续盈利能力究竟如何？未来三年高达89亿元的合计业绩承诺能否兑现？作为互联网公司，它的会计处理是否稳健？
交易方案首次对三六零的业务情况进行了详细披露。
2012年，三六零以免费策略，颠覆、逆袭了当年的杀毒软件龙头金山毒霸，一举成为国内安全工具市场主导者。统计显示，2016年，360安全卫士的市场份额高达91.76%，在这个领域处于绝对垄断地位。
从产品端上看，三六零的产品主要包括五大类：互联网安全产品及服务（如360安全卫士、360杀毒）、信息获取类产品（360搜索、360导航）、内容类产品（360影视大全、360娱乐）、智能硬件（智能摄像机、智能手表）、国家安全及社会安全服务（猎网平台、360 Cert、威胁情报中心、DDoS Mon）。
从商业变现的角度考量，三六零主要依靠的是广告和游戏业务，此外智能硬件也贡献了小部分收入。方案披露，2016年，三六零的互联网广告及服务收入占公司主营业务收入的59.8%，游戏占26.38%，智能硬件占8.12%；2017年上半年，上述三种业务的收入占比分别为72.44%、16.58%和8.77%。
财报显示，三六零业绩一直保持稳健增长。2015年至2017年上半年，三六零分别实现营收93.57亿元、99.04亿元、52.88亿元；净利润分别为13.40亿元、18.72亿元、14.11亿元；扣非净利润分别为10.65亿元、7.44亿元、9.95亿元；经营性现金流量净额分别为24.08亿元、51.57亿元、14.48亿元。值得注意的是，虽然公司2016年扣非净利润有所下降，但是经营性现金流增长显著，显示公司经营状况稳健向好。
值得一提的是，研发费用资本化通常是科技企业进行利润调节的合法工具，但三六零却将技术研发费用全部计入了当期费用，未进行资本化，这样的做法在重研发支出的互联网公司中，堪称一股“清流”。据披露，2014年至2016年，三六零的研发支出分别为28.81亿、31.85亿、22.72亿元，分别占当期营收的37%、34%、23%。相比之下，目前A股不少热门的科技公司，其研发费用资本化率都在50%以上。
投资人有望获丰厚回报
由于奇虎360私有化时高达百亿美元的估值，买方团队多层分销引入了大量投资人。根据此前相关公告，间接参股三六零的A股公司中，中信国安持股量较大，出资额逾20亿元，预计合计持股占比4.46%。其次是天业股份，出资逾6亿元。其余出资2亿元以上的参股上市公司还有中南文化、电广传媒、雅克科技、浙江永强、三七互娱等。
那么，三六零借壳后，A股投资人的回报空间如何？

以中信国安为例。中信国安此前披露，预计对360私有化的投资金额约为4亿美元等值人民币。若按照对应26亿元人民币估算，中信国安持有重组后江南嘉捷的成本仅为9.15元/股，与江南嘉捷停牌前的股价8.79元相当接近。这意味着，江南嘉捷复牌后，中信国安有望获得丰厚的回报。
更值得关注的是，证监会新闻发言人在3日例行发布会上回应360借壳时表示：“证监会支持境外优秀中资企业参与境内上市公司的并购重组，支持符合国家重点行业产业发展方向、掌握核心技术、具有一定规模的境外上市中资企业参与A股公司并购重组，并将对其中涉及的重组交易进行严格要求，严厉打击并购重组中可能涉嫌内幕交易的违法违规行为。”"""

        self.content = '''
        随着新城控股的一纸任命，又一位万达高管选择出走。
11月1日，新城控股发布公告披露，同意聘黄春雷先生任公司副总裁，任期与本届董事会任期相同。
据观点地产新媒体查阅，黄春雷1975年出生，1997年毕业于上海财经大学，获工学学士学位。于新城控股任职前，他先后任职于浪潮软件股份有限公司、上海万申信息产业股份有限公司，美通无线通信（上海）有限公司、微软（中国）有限公司企业咨询部及万达集团股份有限公司等公司，是典型的技术型高管。
同时，这也是继去年陈德力加入新城担任副总裁后，又一位从万达转入新城的高管。2016年8月，新城控股发布公告称，经董事会审议通过，同意聘请陈德力任公司副总裁，分管新城商业管理事业部与资产管理中心。
相比于彼时市场关于陈德力离职时的各种传闻，如今黄春雷的出走显得低调许多。
黄春雷的新城
公开资料显示，在万达时，黄春雷先后担任了集团总裁助理兼信息管理中心常务副总经理、集团总裁助理兼金融集团网络数据中心总经理。
加入新城后，他也将分管集团信息管理中心及创新业务，负责集团信息化建设，包括住宅和商业的信息化将会进行一体化建设。
随着房地产行业从黄金时代进入白银时代，信息化建设被越来越多纳入房企的管理中，王石甚至曾经说过，“搞不懂IT，我就连董事长都辞掉”。
据观点地产新媒体了解，早在2012年，万达内部就开始推行信息化管理，将所有的商业运营通过信息化平台集合完成，以降低人力成本，同时使快速的商业扩展得到保证。
为此，万达集团专门成立了慧云专项工作小组，由商业规划院、信息中心、商管公司等多部门合作，经过五年时间，研发出“慧云”信息管理系统，这也是全球规模最大的商业建筑智能化管理系统，并运用于旗下所有的万达广场中，包括轻资产模式中。
显然，作为万达商业模式中重要的一环，黄春雷此前所在的信息管理中心对万达商业快速扩张起到了重要作用。
无独有偶，在不久前举行的新城商业年会上，陈德力曾表示，目前重要的一个工作是打通新城商业的全产业链，即形成一个贯穿土地获取、规划设计、开发建设、招商运营、资产管理、资产证券化的闭环。其中，系统和人才是最大挑战的一部分。
有市场人士对观点地产新媒体指，此次新城再度挖来万达前高管，昭显了其进一步加快跻身商业地产第一梯队的步伐。
随着黄春雷的加入，这是近年来新城引入的第四位万达高管。除了陈德力，万达商管公司南区营运中心副总经钱文虹也于去年离职，现任新城招商中心总经理一职；此外，新城还挖来了原万达商管综合管理中心副总经理唐剑锋，担任新城商管运营中心总经理。
在新城的规划中，到2020年，公司要实现100座吾悦广场的开业，同时取得百亿租金，进入商业地产第一梯队。
万达商业前高管们
众所周知，万达的人事变动频率向来不低。曾有这样一句话这样形容万达，铁打的营盘，流水的高管。
从内部来看，模块化管理和刚性的制度确保了每年20个万达广场的高速化发展，同时也造成了高管的频繁离职。
在外部环境上，不少商业地产商极力模仿万达时，也在不断挖万达的墙脚，其中不乏带领万达一路扩张的高管们，包括张华容、王寿庆、陈德力、张立洲等，均已悉数离职。
时间回到2011年，张华容从万达离职，加盟红星商业，成为红星美凯龙商业地产新团队中的核心，此前她已在万达供职五年。
观点地产新媒体了解，在张华容加入之初，万达商业正处于摸索阶段，此后万达一路扩张。直到2011年离职时，她共参与了43个万达广场的项目设计和招商工作，职位为万达商业管理副总经理兼招商中心总经理。
张华容之后，曾有“上海王”之称的王寿庆也于翌年选择离开，加入广东创鸿集团担任执行总裁。
2002年正式进入万达集团，主要参与上海项目公司的工作，且在万达内部有着很大的影响力。尤其是在运营上海万达广场上，从奠基到开业仅耗22个月零18天，并引进了沃尔玛等八大主力店，商场开业一年便实现盈利。他由此被业内称为“上海王”。
不过，令人意外的是，在外兜兜转转三年后，王寿庆于2015年11月重回“老东家”，彼时被任命为万达文化产业集团副总裁兼万达主题娱乐有限公司总经理。只是不足一年后，他再次离职，上演了“二进二出万达”的戏码。'''
        self.paragraph = """若交易顺利完成，对投资者来说更为重要的，应是三六零的“生意经”。这家网络安全巨头的业绩和持续盈利能力究竟如何？未来三年高达89亿元的合计业绩承诺能否兑现？作为互联网公司，它的会计处理是否稳健？交易方案首次对三六零的业务情况进行了详细披露。"""

    def tearDown(self):
        pass

    def test_extract(self):
        sumzer = Summarizer()
        abstract, scores = sumzer.extract(self.content, self.title)
        sum_up = 0.0
        for (x,y) in enumerate(abstract):
            print("index: %d >> %s | score: %f" % (x, y, scores[x]))
            sum_up += scores[x]
        print("total: %f" % sum_up)

    def test_keywords(self):
        content = '''11月2日晚间，重庆小康工业集团股份有限公司(以下简称“小康股份”)发布公告称其前期通过全资子公司SFMOTORS收购美国AMG公司民用汽车工厂及相关资产一事已正式完成交割程序。据了解，本次收购顺利完成后，SFMOTORS在保留了AMG给奔驰代工期间的原班运营人马的基础上，将很好地继承AMG现有的技术产能优势及高端品牌车型制造经验，进一步强化其自身实力，使其成为唯一一个中美两地都拥有制造基地的电动车科技企业，这也标志着小康股份创建新能源电动汽车领先品牌在制造环节布局的进一步完善。\n \n　　借力资本夯实新能源战略\n \n　　据了解，小康股份作为国内自主品牌汽车制造企业，一直专注于汽车产业的制造、销售和研发。顺应行业发展趋势和国家政策引导，2016年7月，刚上市的小康股份即提出转型规划，宣布将面向新能源汽车实现战略转型，制定了“创建新能源电动车领先品牌，发展高端智能电动车”的战略。\n \n　　在市场看来，小康股份适时入局新能源汽车领域，是兼具“天时、地利、人和”的明智之举。一方面，小康股份作为集汽车整车及汽车发动机、汽车零部件制造、销售于一体的制造型企业，已具备强大的整车集成的经验与技术开发储备，拥有研产供销全产业链运作经验，以及完善的产品创造流程体系，其专业的生产设备、生产线以及管理运营也具有明显优势；另一方面，随着公司成功登陆资本市场，其资金优势及资源整合能力也给其注入强大的后备支撑力。近日，小康股份发布可转债募集公告，拟募集资金15亿元，将全部投向年产5万辆纯电动乘用车建设项目。据公告显示，该项目总投资25亿元，将于2018年10月完工，计划实现年产5万台系列新能源乘用车和6万套电池PACK的产能目标，预计在项目建设完成并全部达产后每年能给公司带来净利润约2.37亿元。\n \n　　事实上，2016年以来，小康股份借力资本市场的融资及资源整合能力，通过一系列的海外技术和人才资源整合，逐步在新能源产业链包括三电技术、智能驾驶、BMS技术等方面形成了核心优势，此外凭借其多年的整车制造运营经验，其在新能源汽车产品制造能力、供应链和营销网络建设方面也在迅速完善。由此构成了小康股份在新能源汽车领域内独有的竞争优势。今年年初，小康股份获得新能源车独立生产资质的企业，成为国内第8家获此资质的汽车制造企业，顺利入局国内新能源汽车优势制造商阵营。\n \n　　整合全球资源强势发力\n \n　　公开资料显示，小康股份一方面通过整合全球优势资源，迅速完成了公司在新能源汽车领域业务闭环。除了此次顺利完成的AMG收购，小康股份上个月刚宣布其子公司SFMOTORS以3300万美元全资收购美国电池系统公司InEVit，以此优先掌握具有国际领先的新能源电动汽车电池系统核心技术，并将InEvit的创始人(同时是Tesla创始人兼首任CEO)MartinEberhard，及共同创始人-汽车产品机电一体化专家HeinerFees，以及InEVit的CEO、美国硅谷资深投资专家MikeMiskovsky悉数纳入公司麾下，这将为小康股份在新能源汽车业务领域的市场定位、产品规划、品牌推广、商业计划等方面带来全新的理念和执行布局。\n \n　　另一方面，小康股份高度重视企业自身研发团队建设。公司已在美国加州硅谷设立美国总部和研发中心，并引进掌握国际领先电动车技术的核心团队，目前已组建以唐一帆先生为技术与研发带头人的优秀团队负责电动车的研发。据了解，唐一帆先生作为业内电动车技术领军人物之一，曾参与特斯拉Roadster和ModelS电动车三电系统设计，是特斯拉ModelXAWD原型车三电系统的设计者之一，并曾在美国加州硅谷的另一家电动车创新公司Atieva任职，在LucidAir车型上实现了技术的创新和迭代，进一步提升了该车的百公里加速度、最高车速等性能指标。在坐拥AMG和InEVit这两项优质资源后的SFMOTORS也被市场广泛看好，甚至因其同样坐落硅谷、放眼国际主打高端电动车市场、研发团队拥有多名原特斯拉工程师的特性，被不少人誉为“最有可能接近特斯拉的公司”。\n \n　　某市场人士表示，在国内入局新能源汽车的传统车企中，小康股份无疑是做得较好的企业之一。无论是战略规划方面，或是执行落地方面，都是基于对行业发展趋势可把控范围内的果断决判。尤其是公司登陆资本市场以来，充分利用其资源整合能力，迅速完整新能源汽车制造产业链布局，掌握核心技术，占得先发优势。在国家政策支持引导、市场发展态势良好的背景下，小康股份新能源布局非常值得期待。","title":"小康股份(601127)收购AMG顺利交割 借力资本持续发力新能源'''
        sumzer = Summarizer()
        print("*"*20)
        print("* keywords by idf ")
        print("*"*20)     
        keywords, scores = sumzer.keywords(content)  
        for (k, v) in zip(keywords, scores):
            print("word: %s, score: %f" % (k, v))

        print("*"*20)
        print("* keywords by textrank ")
        print("*"*20)
        keywords, scores = sumzer.keywords(self.content, vendor = "textrank")  
        for (k, v) in zip(keywords, scores):
            print("word: %s, score: %f" % (k, v))

    def test_paragraph_to_sentence(self):
        sumzer = Summarizer()
        for x,_ in sumzer.paragraph_to_sentence(self.paragraph):
            print("pop: %s | 标点: %s" %(x, _))

    def test_doc_to_sentences(self):
        sumzer = Summarizer()
        sentences = sumzer.doc_to_sentences(self.content)
        for k,v in enumerate(sentences):
            print("index: %d >> %s" % (k,v))

    def test_evaluate_with_title_single(self):
        print("test_evaluate_with_title_single")
        # content = '''2017第十六届中国国际社会公共安全博览会(以下简称“安博会”)于2017年10月29日至11月1号在深圳会展中心隆重举行,本次展会持续4天。作为具有全球影响力的安防盛会,本届安博会预计将吸引来自150多个国家和地区的13万左右的业界人士前来观展。 AI、物联网、大数据平台等新技术,成为安防新动向。随着人们对安全性要求的提高,以及各级政府大力推进“平安城市”建设的进程,安防监控领域的数据量也随之呈现爆炸式增长。因此,安防行业具备在人工智能方面最完善的基础和最强烈的诉求。在过去的几年,公安、政府、交通这些安防行业的重点目标都已开始积极利用新一代智能安防产品。\r\n　　智慧城市需求旺盛,相关企业持续受益。根据中国产业信息网的数据预测,2017年我国智慧城市市场规模将超过3700亿元,未来五年的复合增长率超过30%,到2021年将达到12000亿元。\r\n　　PPP成为安防发展新模式。根据财政部发布的数据,截至2017年6月末,PPP项目中市政工程、交通运输以及生态建设和环境保护位列项目比例前三名,分别为4732、1756和826个,共占所有入库项目的54%。\r\n　　本次安博会上,各家安防厂商将会展示最新的安防相关产品和技术,A股相关上市公司值得关注:\r\n　　海康威视:国内安防企业龙头,布局人工智能、安防大数据平台。\r\n　　大华股份:智能安防+PPP,紧跟海康威视处于安防领域第一梯队。\r\n　　立昂技术:新疆本地安防企业,受益于新疆基础建设与维稳的需求,公司业绩大幅增长。\r\n　　苏州科达:政府部门视频会议业内领先,长期受益于国产替代政策\r\n　　易华录:专注于智能交通行业,通过PPP拓展到智慧城市领域。 熙菱信息:新疆本地安防企业,受益于新疆基础建设与维稳的需求,打造公告安全领域实战产品。\r\n　　重点推荐组合\r\n　　海康威视、立昂技术、广联达、用友网络、大华股份、汉得信息。\r\n　　风险提示:安防相关技术和业务进展不及预期。\r\n\r    转载自：新时代证券股份有限公司 '''
        content = '''11月2日晚间，重庆小康工业集团股份有限公司(以下简称“小康股份”)发布公告称其前期通过全资子公司SFMOTORS收购美国AMG公司民用汽车工厂及相关资产一事已正式完成交割程序。据了解，本次收购顺利完成后，SFMOTORS在保留了AMG给奔驰代工期间的原班运营人马的基础上，将很好地继承AMG现有的技术产能优势及高端品牌车型制造经验，进一步强化其自身实力，使其成为唯一一个中美两地都拥有制造基地的电动车科技企业，这也标志着小康股份创建新能源电动汽车领先品牌在制造环节布局的进一步完善。
 
　　借力资本夯实新能源战略
 
　　据了解，小康股份作为国内自主品牌汽车制造企业，一直专注于汽车产业的制造、销售和研发。顺应行业发展趋势和国家政策引导，2016年7月，刚上市的小康股份即提出转型规划，宣布将面向新能源汽车实现战略转型，制定了“创建新能源电动车领先品牌，发展高端智能电动车”的战略。
 
　　在市场看来，小康股份适时入局新能源汽车领域，是兼具“天时、地利、人和”的明智之举。一方面，小康股份作为集汽车整车及汽车发动机、汽车零部件制造、销售于一体的制造型企业，已具备强大的整车集成的经验与技术开发储备，拥有研产供销全产业链运作经验，以及完善的产品创造流程体系，其专业的生产设备、生产线以及管理运营也具有明显优势；另一方面，随着公司成功登陆资本市场，其资金优势及资源整合能力也给其注入强大的后备支撑力。近日，小康股份发布可转债募集公告，拟募集资金15亿元，将全部投向年产5万辆纯电动乘用车建设项目。据公告显示，该项目总投资25亿元，将于2018年10月完工，计划实现年产5万台系列新能源乘用车和6万套电池PACK的产能目标，预计在项目建设完成并全部达产后每年能给公司带来净利润约2.37亿元。
 
　　事实上，2016年以来，小康股份借力资本市场的融资及资源整合能力，通过一系列的海外技术和人才资源整合，逐步在新能源产业链包括三电技术、智能驾驶、BMS技术等方面形成了核心优势，此外凭借其多年的整车制造运营经验，其在新能源汽车产品制造能力、供应链和营销网络建设方面也在迅速完善。由此构成了小康股份在新能源汽车领域内独有的竞争优势。今年年初，小康股份获得新能源车独立生产资质的企业，成为国内第8家获此资质的汽车制造企业，顺利入局国内新能源汽车优势制造商阵营。
 
　　整合全球资源强势发力
 
　　公开资料显示，小康股份一方面通过整合全球优势资源，迅速完成了公司在新能源汽车领域业务闭环。除了此次顺利完成的AMG收购，小康股份上个月刚宣布其子公司SFMOTORS以3300万美元全资收购美国电池系统公司InEVit，以此优先掌握具有国际领先的新能源电动汽车电池系统核心技术，并将InEvit的创始人(同时是Tesla创始人兼首任CEO)MartinEberhard，及共同创始人-汽车产品机电一体化专家HeinerFees，以及InEVit的CEO、美国硅谷资深投资专家MikeMiskovsky悉数纳入公司麾下，这将为小康股份在新能源汽车业务领域的市场定位、产品规划、品牌推广、商业计划等方面带来全新的理念和执行布局。
 
　　另一方面，小康股份高度重视企业自身研发团队建设。公司已在美国加州硅谷设立美国总部和研发中心，并引进掌握国际领先电动车技术的核心团队，目前已组建以唐一帆先生为技术与研发带头人的优秀团队负责电动车的研发。据了解，唐一帆先生作为业内电动车技术领军人物之一，曾参与特斯拉Roadster和ModelS电动车三电系统设计，是特斯拉ModelXAWD原型车三电系统的设计者之一，并曾在美国加州硅谷的另一家电动车创新公司Atieva任职，在LucidAir车型上实现了技术的创新和迭代，进一步提升了该车的百公里加速度、最高车速等性能指标。在坐拥AMG和InEVit这两项优质资源后的SFMOTORS也被市场广泛看好，甚至因其同样坐落硅谷、放眼国际主打高端电动车市场、研发团队拥有多名原特斯拉工程师的特性，被不少人誉为“最有可能接近特斯拉的公司”。
 
　　某市场人士表示，在国内入局新能源汽车的传统车企中，小康股份无疑是做得较好的企业之一。无论是战略规划方面，或是执行落地方面，都是基于对行业发展趋势可把控范围内的果断决判。尤其是公司登陆资本市场以来，充分利用其资源整合能力，迅速完整新能源汽车制造产业链布局，掌握核心技术，占得先发优势。在国家政策支持引导、市场发展态势良好的背景下，小康股份新能源布局非常值得期待。'''
        # title = "计算机:关注AI、物联网等安防技术新动向"
        title = "小康股份(601127)收购AMG顺利交割 借力资本持续发力新能源"
        sumzer = Summarizer()
        abstract = sumzer.extract(content, title)
        print("extract:", abstract)

    def test_doc_to_paragraphs(self):
        sumzer = Summarizer()
        paragraphs = sumzer.doc_to_paragraphs(self.content)
        print("paragraphs len:", len(paragraphs))

        for (k, v) in enumerate(paragraphs):
            print("index :", k)
            print(v + "\n")

    def test_norm_1(self):
        print("test_norm_1")
        print(normalize([0.1, 0.2, 0.3]))

    def test_bm25(self):
        print("test_bm25")
        # content = '''2017第十六届中国国际社会公共安全博览会(以下简称“安博会”)于2017年10月29日至11月1号在深圳会展中心隆重举行,本次展会持续4天。作为具有全球影响力的安防盛会,本届安博会预计将吸引来自150多个国家和地区的13万左右的业界人士前来观展。 AI、物联网、大数据平台等新技术,成为安防新动向。随着人们对安全性要求的提高,以及各级政府大力推进“平安城市”建设的进程,安防监控领域的数据量也随之呈现爆炸式增长。因此,安防行业具备在人工智能方面最完善的基础和最强烈的诉求。在过去的几年,公安、政府、交通这些安防行业的重点目标都已开始积极利用新一代智能安防产品。\r\n　　智慧城市需求旺盛,相关企业持续受益。根据中国产业信息网的数据预测,2017年我国智慧城市市场规模将超过3700亿元,未来五年的复合增长率超过30%,到2021年将达到12000亿元。\r\n　　PPP成为安防发展新模式。根据财政部发布的数据,截至2017年6月末,PPP项目中市政工程、交通运输以及生态建设和环境保护位列项目比例前三名,分别为4732、1756和826个,共占所有入库项目的54%。\r\n　　本次安博会上,各家安防厂商将会展示最新的安防相关产品和技术,A股相关上市公司值得关注:\r\n　　海康威视:国内安防企业龙头,布局人工智能、安防大数据平台。\r\n　　大华股份:智能安防+PPP,紧跟海康威视处于安防领域第一梯队。\r\n　　立昂技术:新疆本地安防企业,受益于新疆基础建设与维稳的需求,公司业绩大幅增长。\r\n　　苏州科达:政府部门视频会议业内领先,长期受益于国产替代政策\r\n　　易华录:专注于智能交通行业,通过PPP拓展到智慧城市领域。 熙菱信息:新疆本地安防企业,受益于新疆基础建设与维稳的需求,打造公告安全领域实战产品。\r\n　　重点推荐组合\r\n　　海康威视、立昂技术、广联达、用友网络、大华股份、汉得信息。\r\n　　风险提示:安防相关技术和业务进展不及预期。\r\n\r    转载自：新时代证券股份有限公司 '''
        content = '''11月2日晚间，重庆小康工业集团股份有限公司(以下简称“小康股份”)发布公告称其前期通过全资子公司SFMOTORS收购美国AMG公司民用汽车工厂及相关资产一事已正式完成交割程序。据了解，本次收购顺利完成后，SFMOTORS在保留了AMG给奔驰代工期间的原班运营人马的基础上，将很好地继承AMG现有的技术产能优势及高端品牌车型制造经验，进一步强化其自身实力，使其成为唯一一个中美两地都拥有制造基地的电动车科技企业，这也标志着小康股份创建新能源电动汽车领先品牌在制造环节布局的进一步完善。
 
　　借力资本夯实新能源战略
 
　　据了解，小康股份作为国内自主品牌汽车制造企业，一直专注于汽车产业的制造、销售和研发。顺应行业发展趋势和国家政策引导，2016年7月，刚上市的小康股份即提出转型规划，宣布将面向新能源汽车实现战略转型，制定了“创建新能源电动车领先品牌，发展高端智能电动车”的战略。
 
　　在市场看来，小康股份适时入局新能源汽车领域，是兼具“天时、地利、人和”的明智之举。一方面，小康股份作为集汽车整车及汽车发动机、汽车零部件制造、销售于一体的制造型企业，已具备强大的整车集成的经验与技术开发储备，拥有研产供销全产业链运作经验，以及完善的产品创造流程体系，其专业的生产设备、生产线以及管理运营也具有明显优势；另一方面，随着公司成功登陆资本市场，其资金优势及资源整合能力也给其注入强大的后备支撑力。近日，小康股份发布可转债募集公告，拟募集资金15亿元，将全部投向年产5万辆纯电动乘用车建设项目。据公告显示，该项目总投资25亿元，将于2018年10月完工，计划实现年产5万台系列新能源乘用车和6万套电池PACK的产能目标，预计在项目建设完成并全部达产后每年能给公司带来净利润约2.37亿元。
 
　　事实上，2016年以来，小康股份借力资本市场的融资及资源整合能力，通过一系列的海外技术和人才资源整合，逐步在新能源产业链包括三电技术、智能驾驶、BMS技术等方面形成了核心优势，此外凭借其多年的整车制造运营经验，其在新能源汽车产品制造能力、供应链和营销网络建设方面也在迅速完善。由此构成了小康股份在新能源汽车领域内独有的竞争优势。今年年初，小康股份获得新能源车独立生产资质的企业，成为国内第8家获此资质的汽车制造企业，顺利入局国内新能源汽车优势制造商阵营。
 
　　整合全球资源强势发力
 
　　公开资料显示，小康股份一方面通过整合全球优势资源，迅速完成了公司在新能源汽车领域业务闭环。除了此次顺利完成的AMG收购，小康股份上个月刚宣布其子公司SFMOTORS以3300万美元全资收购美国电池系统公司InEVit，以此优先掌握具有国际领先的新能源电动汽车电池系统核心技术，并将InEvit的创始人(同时是Tesla创始人兼首任CEO)MartinEberhard，及共同创始人-汽车产品机电一体化专家HeinerFees，以及InEVit的CEO、美国硅谷资深投资专家MikeMiskovsky悉数纳入公司麾下，这将为小康股份在新能源汽车业务领域的市场定位、产品规划、品牌推广、商业计划等方面带来全新的理念和执行布局。
 
　　另一方面，小康股份高度重视企业自身研发团队建设。公司已在美国加州硅谷设立美国总部和研发中心，并引进掌握国际领先电动车技术的核心团队，目前已组建以唐一帆先生为技术与研发带头人的优秀团队负责电动车的研发。据了解，唐一帆先生作为业内电动车技术领军人物之一，曾参与特斯拉Roadster和ModelS电动车三电系统设计，是特斯拉ModelXAWD原型车三电系统的设计者之一，并曾在美国加州硅谷的另一家电动车创新公司Atieva任职，在LucidAir车型上实现了技术的创新和迭代，进一步提升了该车的百公里加速度、最高车速等性能指标。在坐拥AMG和InEVit这两项优质资源后的SFMOTORS也被市场广泛看好，甚至因其同样坐落硅谷、放眼国际主打高端电动车市场、研发团队拥有多名原特斯拉工程师的特性，被不少人誉为“最有可能接近特斯拉的公司”。
 
　　某市场人士表示，在国内入局新能源汽车的传统车企中，小康股份无疑是做得较好的企业之一。无论是战略规划方面，或是执行落地方面，都是基于对行业发展趋势可把控范围内的果断决判。尤其是公司登陆资本市场以来，充分利用其资源整合能力，迅速完整新能源汽车制造产业链布局，掌握核心技术，占得先发优势。在国家政策支持引导、市场发展态势良好的背景下，小康股份新能源布局非常值得期待。'''
        # title = "计算机:关注AI、物联网等安防技术新动向"
        title = "小康股份(601127)收购AMG顺利交割 借力资本持续发力新能源"
        sumz = Summarizer()
        

def test():
    unittest.main()

if __name__ == '__main__':
    test()
