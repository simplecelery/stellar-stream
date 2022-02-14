import re
import json

sites = [
    {
        "name": "斗鱼直播",
        "realurl": "douyu1",
        "danmu": "douyu.Douyu",
        "rules": [r"^https://www.douyu.com/([0-9A-Za-z]*)$", r"https://www.douyu.com/topic/\w*\?rid=([0-9A-Za-z]*)"]
    },
    {
        "name": "虎牙直播",
        "realurl": "huya",
        "danmu": "huya.Huya",
        "rules": [r"https://(?:www|m).huya.com/([0-9A-Za-z]*)"]
    },
    {
        "name": "龙珠直播",
        "realurl": "longzhu",
        "rules": r"https://star.longzhu.com/([0-9A-Za-z]*)",
    },
    {
        "name": "花椒直播",
        "realurl": "huajiao",
        "rules": r"https://star.huajiao.com/l/([0-9A-Za-z]*)",
    },
    {
        "name": "中国体育",
        "realurl": "zhibotv",
        "rules": r"http://v.zhibo.tv/([0-9A-Za-z]*)",
    },
    {
        "name": "西瓜视频",
        "realurl": "ixigua",
        "rules": r"https://live.ixigua.com/([0-9A-Za-z]*)",
        "key": lambda x: json.loads(x)[0]['FlvUrl']
    },
    {
        "name": "企鹅电竞",
        "realurl": "egame",
        "rules": r"https://egame.qq.com/([0-9A-Za-z]*)"
    },
    {
        "name": "棉花糖",
        "realurl": "2cq",
        "rules": r"https://www.2cq.com/([0-9A-Za-z]*)"
    },
    {
        "name": "bilibili",
        "realurl": "bilibili",
        "danmu": "bilibili.Bilibili",
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


