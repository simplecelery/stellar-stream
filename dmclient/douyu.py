
import _thread
import time
import re
import json
import requests

from struct import pack

from . import DanmuClient


class Douyu(DanmuClient):
    wss_url = 'wss://danmuproxy.douyu.com:8503/'
    heartbeat = b'\x14\x00\x00\x00\x14\x00\x00\x00\xb1\x02\x00\x00\x74\x79\x70\x65\x40\x3d\x6d\x72\x6b\x6c\x2f\x00'
    heartbeatInterval = 60

    def get_ws_info(self, url):
        rules = [r"^https://www.douyu.com/([0-9A-Za-z]*)$", r"https://www.douyu.com/topic/\w*\?rid=([0-9A-Za-z]*)"]
        room_id = ''
        for rule in rules:
            m = re.match(rule, url)
            if m:
                room_id = m.group(1)
                break
        if not room_id:
            raise RuntimeError('invalid douyu url')
        resp = requests.get(f'https://m.douyu.com/{room_id}')
        room_page = resp.text
        room_id = re.findall(r'"rid":(\d{1,7})', room_page)[0]        
        reg_datas = []
        data = f'type@=loginreq/roomid@={room_id}/'
        s = pack('i', 9 + len(data)) * 2
        s += b'\xb1\x02\x00\x00'  # 689
        s += data.encode('ascii') + b'\x00'
        reg_datas.append(s)
        data = f'type@=joingroup/rid@={room_id}/gid@=-9999/'
        s = pack('i', 9 + len(data)) * 2
        s += b'\xb1\x02\x00\x00'  # 689
        s += data.encode('ascii') + b'\x00'
        reg_datas.append(s)
        return Douyu.wss_url, reg_datas

    def decode_msg(self, data):
        msgs = []
        for msg in re.findall(b'(type@=.*?)\x00', data):
            try:
                msg = msg.replace(b'@=', b'":"').replace(b'/', b'","')
                msg = msg.replace(b'@A', b'@').replace(b'@S', b'/')
                msg = json.loads((b'{"' + msg[:-2] + b'}').decode('utf8', 'ignore'))
                msg['name'] = msg.get('nn', '')
                msg['content'] = msg.get('txt', '')
                msg['msg_type'] = {'dgb': 'gift', 'chatmsg': 'danmaku',
                                   'uenter': 'enter'}.get(msg['type'], 'other')
                msgs.append(msg)
            except Exception as e:
                pass
        return msgs


def main():
    # websocket.enableTrace(True)
    client = Douyu()
    client.start('https://www.douyu.com/48699')
    client.run_forever()
    print("the end")

if __name__ == "main":
    main()