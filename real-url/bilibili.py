# 获取哔哩哔哩直播的真实流媒体地址，默认获取直播间提供的最高画质
# qn=150高清
# qn=250超清
# qn=400蓝光
# qn=10000原画
import re

import requests


class BiliBili:

    def __init__(self, rid):
        """
        有些地址无法在PotPlayer播放，建议换个播放器试试
        Args:
            rid:
        """
        self.rid = rid

    def get_real_url(self):
        self.header = {
            'User-Agent': 'Mozilla/5.0 (iPod; CPU iPhone OS 14_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, '
                          'like Gecko) CriOS/87.0.4280.163 Mobile/15E148 Safari/604.1',
        }
        # 先获取直播状态和真实房间号
        r_url = 'http://api.live.bilibili.com/room/v1/Room/playUrl'
        param = {
            'cid': self.rid,
            'qn': 10000,
            'platform': 'web'
        }
        with requests.Session() as self.s:
            res = self.s.get(r_url, headers=self.header, params=param).json()
        if res['code'] != 0:
            raise Exception(f'bilibili {self.rid} {res["message"]}')
        return res["data"]["durl"][0]["url"]


def get_real_url(rid):
    try:
        bilibili = BiliBili(rid)
        return bilibili.get_real_url()
    except Exception as e:
        print('Exception：', e)
        return False


if __name__ == '__main__':
    r = input('请输入bilibili直播房间号：\n')
    print(get_real_url(r))
