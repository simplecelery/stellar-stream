
import websocket
import threading
import time 


class DanmuClient:
    def __init__(self):
        self.reg_datas = None
        self.ws = None
        self.cb = None

    def start(self, url, cb):
        ws_url, self.reg_datas = self.get_ws_info(url)
        self.cb = cb
        self.ws = self.connect(ws_url)

    def stop(self):
        self.ws.close()
        print("self.ws.close()~~~~~~~~~~~~~~")

    def connect(self, ws_url):
        return websocket.WebSocketApp(ws_url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close)

    def on_open(self, ws):
        print("### opened ###")
        for reg_data in self.reg_datas:
            self.ws.send(reg_data)
        t = threading.Thread(target=self.heartbeat_thread, daemon=True)
        t.start()

    def on_message(self, ws, message):
        msgs = self.decode_msg(message)
        for m in msgs:
            # print(m)
            if m["msg_type"] == 'danmaku':
                if self.cb:
                    self.cb(m["content"])
                

    def on_error(self, ws, error):
        print(error)

    def on_close(self, ws, close_status_code, close_msg):
        print(f"### closed ### {close_status_code=}, {close_msg=}")
        self.ws = None

    def heartbeat_thread(self):        
        t = 0.0
        while not self.ws is None:
            if time.time() - t > self.heartbeatInterval:
                self.ws.send(self.heartbeat)
                t = time.time()
                print(f'send heartbeat~~~~~~~~~~~~~~~')
            time.sleep(0.1)

    def run(self):
        t = threading.Thread(target=self.ws.run_forever, daemon=True)
        t.start()



