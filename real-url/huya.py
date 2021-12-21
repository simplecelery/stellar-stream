# 获取虎牙直播的真实流媒体地址。
# 虎牙"一起看"频道的直播间可能会卡顿，尝试将返回地址 tx.hls.huya.com 中的 tx 改为 bd、migu-bd。

import requests
import re
import base64
import urllib.parse
import hashlib
import time
import json

def live(e):
    i, b = e.split('?')
    r = i.split('/')
    s = re.sub(r'.(flv|m3u8)', '', r[-1])
    c = b.split('&', 3)
    c = [i for i in c if i != '']
    n = {i.split('=')[0]: i.split('=')[1] for i in c}
    fm = urllib.parse.unquote(n['fm'])
    u = base64.b64decode(fm).decode('utf-8')
    p = u.split('_')[0]
    f = str(int(time.time() * 1e7))
    l = n['wsTime']
    t = '0'
    h = '_'.join([p, t, s, f, l])
    m = hashlib.md5(h.encode('utf-8')).hexdigest()
    y = c[-1]
    url = "{}?wsSecret={}&wsTime={}&u={}&seqid={}&{}".format(i, m, l, t, f, y)
    return url

class HuYa:
    def __init__(self, rid):
        self.rid = rid

    def get_real_url(self):        
        return get_real_url(self.rid)


def get_real_url(room_id):
    try:
        room_url = 'https://m.huya.com/' + str(room_id)
        header = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/75.0.3770.100 Mobile Safari/537.36 '
        }
        response = requests.get(url=room_url, headers=header).text
        liveLineUrl = re.findall(r'"liveLineUrl":"([\s\S]*?)",', response)[0]
        liveline = base64.b64decode(liveLineUrl).decode('utf-8')
        if liveline:
            if 'replay' in liveline:
                return liveline
            else:
                liveline = live(liveline)
                real_url = ("https:" + liveline).replace("hls", "flv").replace("m3u8", "flv")
        else:
            raise Exception('未开播或直播间不存在')
    except:
        raise 
        raise Exception('未开播或直播间不存在')
    return real_url


if __name__ == '__main__':
    rid = input('输入虎牙直播房间号：\n')
    print(get_real_url(rid))