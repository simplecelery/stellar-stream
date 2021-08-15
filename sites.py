import re
import json

sites = [
    {
        "name": "斗鱼直播",
        "module": "douyu1",
        "rules": [r"^https://www.douyu.com/([0-9A-Za-z]*)$", r"https://www.douyu.com/topic/\w*\?rid=([0-9A-Za-z]*)"]
    },
    {
        "name": "虎牙直播",
        "module": "huya",
        "rules": r"https://www.huya.com/([0-9A-Za-z]*)",
        "key": 'al_flv'
    },
    {
        "name": "龙珠直播",
        "module": "longzhu",
        "rules": r"https://star.longzhu.com/([0-9A-Za-z]*)",
    },
    {
        "name": "花椒直播",
        "module": "huajiao",
        "rules": r"https://star.huajiao.com/l/([0-9A-Za-z]*)",
    },
    {
        "name": "中国体育",
        "module": "zhibotv",
        "rules": r"http://v.zhibo.tv/([0-9A-Za-z]*)",
    },
    {
        "name": "西瓜视频",
        "module": "ixigua",
        "rules": r"https://live.ixigua.com/([0-9A-Za-z]*)",
        "key": lambda x: json.loads(x)[0]['FlvUrl']
    },
    {
        "name": "企鹅电竞",
        "module": "egame",
        "rules": r"https://egame.qq.com/([0-9A-Za-z]*)"
    },
    {
        "name": "棉花糖",
        "module": "2cq",
        "rules": r"https://www.2cq.com/([0-9A-Za-z]*)"
    },
    {
        "name": "bilibili",
        "module": "bilibili",
        "rules": r"https://live.bilibili.com/([0-9A-Za-z]*)"
    }
]

def match(url):
    for site in sites:
        rules = site['rules']
        if type(rules) is str:
            rules = [rules]
        for rule in rules:
            m = re.match(rule, url)
            if m:
                return m.group(1), site
    return None, None

def main():
    url = "https://www.douyu.com/8152547"
    print(match(url))

if __name__ == "__main__":
    # main()
    url = "https://www.douyu.com/8152547"
    #url = "https://www.douyu.com/topic/bfcxdjj?rid=48699"
    m = re.match(r"^https://www.douyu.com/([0-9A-Za-z]*)$", url)
    m and print(m.group(1))


