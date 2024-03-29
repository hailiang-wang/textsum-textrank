---
title: 文本摘要API文档
author: Hai Liang Wang
header: 文本摘要API文档
footer: Business Confidentials
geometry: margin=1in
abstract: 对新闻文本自动提取摘要，可按照文章比例或字数限制摘要长度。
---

# textsum-textrank
自动摘要

## Usage

src/summarizer.py
```
sm = summarizer.Summarizer
abstract, scores = sm.extract(content, title, rate)
```

## Start

```
admin/run.sh
```

## API

### request
``` {ms}
POST /api/summary HTTP/1.1
Host: 127.0.0.1:10030
Headers:
    Content-Type: application/json; charset=utf-8
    Accept: application/json
Body:
    {"content": "中国家庭贷款、存款比最高的是福建，高达105%，而最低的山西仅为20%。为啥差距这么大？虽然，去年至今，金融系统、地方政府、企业合力演绎了经济去杠杆。但近来小额贷款的火爆，让居民家庭杠杆率问题显现，中国家庭负债有多重?根据西南财经大学与中腾信联合发布的《中国工薪阶层信贷发展报告》显示，中国城镇家庭负债总额占家庭资产总额比例，从2013年的4.5%到2015年的5.0%，再增至2017年的5.5%。根据国家资产负债表研究中心11月下旬发布《三季度中国去杠杆进程报告》指出，中国家庭贷款、存款比，从去年底的44.8%上升到三季度的48.6%，合计今年前三个季度上升了3.8个百分点。居民部门(经济中指由所有常住居民住户组成的部门)的杠杆率继续攀升。中国家庭高负债主要是被城市房产“绑架”。3季度末，居民整体未还贷款总额为39.1万亿，其中个人购房贷款余额为21.1万亿，占总贷款余额的54%。然而，但不同地区、不同年龄段家庭之间显现出较大差异。中国家庭贷款、存款比最高的是福建，高达105%，而最低的山西仅为20%。",
    "title": "中国家庭债务越来越高，东部、80后、工薪阶层负债最重",
    "rate": 140
    }
```

content（必填）带抽取摘要的目标内容。

title (选填) 原文标题，对摘要具有正向的影响，建议请求时添加。

rate（选填）代表生成文档的长度，当rate < 1 时，返回长度为 （全文长度*rate），当 rate >= 1时，代表字数。rate 默认为140。比如，rate = 0.5，则摘要长度为全文的一半；rate = 140，则摘要长度为140字。 

### response

* 正常返回
``` {ms}
{"data": "中国家庭贷款、存款比最高的是福建,高达105%,而最低的山西仅为20%。为啥差距这么大?去年至今,金融系统、地方政府、企业合力演绎了经济去杠杆。但近来小额贷款的火爆,让居民家庭杠杆率问题显现,中国家庭负债有多重?中国家庭高负债主要是被城市房产“绑架”。但不同地区、不同年龄段家庭之间显现出较大差异。", "rc": 1}
```

* 异常返回
``` {ms}
{
    "rc": 0,
    "error": "MSG"
}
```
rc不为1或者statusCode不为200为异常返回。