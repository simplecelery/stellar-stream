import re
import json

sites = [
    {
        "name": "斗鱼直播",
        "module": "douyu1",
        "rule": r"https://www.douyu.com/([0-9A-Za-z]*)"
    },
    {
        "name": "虎牙直播",
        "module": "huya",
        "rule": r"https://www.huya.com/([0-9A-Za-z]*)",
        "key": 'al_flv'
    },
    {
        "name": "龙珠直播",
        "module": "longzhu",
        "rule": r"https://star.longzhu.com/([0-9A-Za-z]*)",
    },
    {
        "name": "花椒直播",
        "module": "huajiao",
        "rule": r"https://star.huajiao.com/l/([0-9A-Za-z]*)",
    },
    {
        "name": "中国体育",
        "module": "zhibotv",
        "rule": r"http://v.zhibo.tv/([0-9A-Za-z]*)",
    },
    {
        "name": "西瓜视频",
        "module": "ixigua",
        "rule": r"https://live.ixigua.com/([0-9A-Za-z]*)",
        "key": lambda x: json.loads(x)[0]['FlvUrl']
    },
    {
        "name": "企鹅电竞",
        "module": "egame",
        "rule": r"https://egame.qq.com/([0-9A-Za-z]*)"
    },
    {
        "name": "棉花糖",
        "module": "2cq",
        "rule": r"https://www.2cq.com/([0-9A-Za-z]*)"
    },
    {
        "name": "bilibili",
        "module": "bilibili",
        "rule": r"https://live.bilibili.com/([0-9A-Za-z]*)"
    }
]

def match(url):
    for site in sites:
        m = re.match(site['rule'], url)
        if m:
            return m.group(1), site
    return None, None