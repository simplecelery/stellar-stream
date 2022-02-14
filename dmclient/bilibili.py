import json
import random
import zlib
import requests

from struct import pack, unpack
from . import DanmuClient


class Bilibili(DanmuClient):
    wss_url = 'wss://broadcastlv.chat.bilibili.com/sub'
    heartbeat = b'\x00\x00\x00\x1f\x00\x10\x00\x01\x00\x00\x00\x02\x00\x00\x00\x01\x5b\x6f\x62\x6a\x65\x63\x74\x20' \
                b'\x4f\x62\x6a\x65\x63\x74\x5d '
    heartbeatInterval = 60

    def get_ws_info(self, url):
        url = 'https://api.live.bilibili.com/room/v1/Room/room_init?id=' + url.split('/')[-1]
        reg_datas = []

        resp = requests.get(url) 
        room_json = json.loads(resp.text)
        room_id = room_json['data']['room_id']
        data = json.dumps({
            'roomid': room_id,
            'uid': int(1e14 + 2e14 * random.random()),
            'protover': 1
        }, separators=(',', ':')).encode('ascii')
        data = (pack('>i', len(data) + 16) + b'\x00\x10\x00\x01' +
                pack('>i', 7) + pack('>i', 1) + data)
        reg_datas.append(data)
        return Bilibili.wss_url, reg_datas


    def decode_msg(self, data):
        dm_list_compressed = []
        dm_list = []
        ops = []
        msgs = []
        while True:
            try:
                packetLen, headerLen, ver, op, seq = unpack('!IHHII', data[0:16])
            except Exception as e:
                break
            if len(data) < packetLen:
                break
            if ver == 1 or ver == 0:
                ops.append(op)
                dm_list.append(data[16:packetLen])
            elif ver == 2:
                dm_list_compressed.append(data[16:packetLen])
            if len(data) == packetLen:
                data = b''
                break
            else:
                data = data[packetLen:]

        for dm in dm_list_compressed:
            d = zlib.decompress(dm)
            while True:
                try:
                    packetLen, headerLen, ver, op, seq = unpack('!IHHII', d[0:16])
                except Exception as e:
                    break
                if len(d) < packetLen:
                    break
                ops.append(op)
                dm_list.append(d[16:packetLen])
                if len(d) == packetLen:
                    d = b''
                    break
                else:
                    d = d[packetLen:]

        for i, d in enumerate(dm_list):
            try:
                msg = {}
                if ops[i] == 5:
                    j = json.loads(d)
                    msg['msg_type'] = {
                        'SEND_GIFT': 'gift',
                        'DANMU_MSG': 'danmaku',
                        'WELCOME': 'enter',
                        'NOTICE_MSG': 'broadcast',
                        'LIVE_INTERACTIVE_GAME': 'interactive_danmaku'  # 新增互动弹幕，经测试与弹幕内容一致
                    }.get(j.get('cmd'), 'other')

                    # 2021-06-03 bilibili 字段更新, 形如 DANMU_MSG:4:0:2:2:2:0
                    if msg.get('msg_type', 'UNKNOWN').startswith('DANMU_MSG'):
                        msg['msg_type'] = 'danmaku'

                    if msg['msg_type'] == 'danmaku':
                        msg['name'] = (j.get('info', ['', '', ['', '']])[2][1]
                                       or j.get('data', {}).get('uname', ''))
                        msg['content'] = j.get('info', ['', ''])[1]
                    elif msg['msg_type'] == 'interactive_danmaku':
                        msg['name'] = j.get('data', {}).get('uname', '')
                        msg['content'] = j.get('data', {}).get('msg', '')
                    elif msg['msg_type'] == 'broadcast':
                        msg['type'] = j.get('msg_type', 0)
                        msg['roomid'] = j.get('real_roomid', 0)
                        msg['content'] = j.get('msg_common', 'none')
                        msg['raw'] = j
                    else:
                        msg['content'] = j
                else:
                    msg = {'name': '', 'content': d, 'msg_type': 'other'}
                msgs.append(msg)
            except Exception as e:
                pass

        return msgs


def main():
    # websocket.enableTrace(True)
    client = Bilibili()
    client.start('https://live.bilibili.com/21589042?hotRank=0&session_id=b1410468df74fcf874ec6463eb52ead1_B4449955-0E38-4160-A2DB-17CC26ABF060')
    client.run_forever()
    print("the end")

if __name__ == "main":
    main()