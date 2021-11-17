import traceback
import StellarPlayer
import importlib
import requests
import threading
import json
import time
import inspect
import os
import sys


from bs4 import BeautifulSoup as bs
from .sites import match

plugin_dir = os.path.dirname(__file__)
sys.path.append(plugin_dir) # for js2py


class MyPlugin(StellarPlayer.IStellarPlayerPlugin):
    def __init__(self,player:StellarPlayer.IStellarPlayer):
        super().__init__(player)
        self.q = ''
        self.result = [
        ]
        self.favs = [
        ]
        self.stop_flag = False
        self.load_favs()
        self.check_thread = None
        self.danmu = None
        self.page_url = ''
        self.real_url = ''
        self.danmuShow = True

    def handleRequest(self, method, args):
        if method == 'onPlay':
            print('---------------onPlay')
            url, = args
            if self.real_url == url:
                if self.danmu:
                    self.danmu.stop()
                    self.danmu = None
                self.danmu = self.create_damnu_client(self.page_url)
                if self.danmu:
                    self.danmu.start(self.page_url, self.on_danmu)
                    self.danmu.run()
        elif method == 'onStopPlay':
            print('---------------onStop')
            if self.danmu:
                print('self.danmu.stop')
                self.danmu.stop()
                self.danmu = None
                self.player.clearDanmu()
        else:
            print(f'handleRequest {method=} {args=}')

    def show(self): 
        result_layout = [
            [
                {
                    'group': [
                        {'type':'label','name':'name'},
                        {'type':'label','name':'url'},
                    ],
                    'dir':'vertical',
                },                
                {'type':'link','name':'收藏','width':50, '@click': 'on_add_fav_click'},
            ]
        ]
        favs_layout = [            
            [   
                {
                   'group': [
                        {'type':'label','name':'name'},
                        {'type':'label','name':'url'},
                    ],
                    'dir':'vertical',
                },
                {'type':'label', 'name':'online', 'width':100},
                {'type':'link','name':'播放','width':50, '@click': 'on_play_fav_click'},
                {'type':'link','name':'删除','width':50, '@click': 'on_del_fav_click'},
            ]
        ]     
        controls = [
            {'type':'space','height':20},
            {
                'group': [
                    {'type':'space'},
                    {'type':'edit','name':'search','height':30, 'width':0.6, 'label': ' ', '@input': 'on_search_input', ':value': 'q'},  
                    {'type':'button','name':'播放', 'height':30, 'width':0.1, '@click': 'on_play_click'},  
                    {'type':'check', 'name':'显示弹幕', '@click': 'on_toggle_danmu_click', ':value': 'danmuShow'},
                    {'type':'space'},
                ],
                'height':30
            },            
            {'type':'space', 'height':20},

            {  
                'group': [
                    {'type':'space'},
                    {
                        'group': [
                            {'type':'list','name':'result', 'height': 48, 'itemheight':48, 'itemlayout': result_layout, ':value': 'result','marginSize':5},
                            {'type':'space', 'height':10 },   
                            {'type':'label','name': '收藏列表', 'height':30},  
                            {'type':'list','name':'favs', 'itemheight':48, 'itemlayout': favs_layout, ':value': 'favs','marginSize':5, 'separator': True},                              
                        ],
                        'dir':'vertical',
                        'width': 0.9,
                    },                    
                    {'type':'space'}
                ],
                'width': 1.0
            }
        ]

        if self.check_thread is None:
            print("create checking thread")
            self.check_thread = threading.Thread(target=self.check_thread_func, daemon=True)
            self.check_thread.start()

        self.player.showDanmu(self.danmuShow)        
        self.doModal('main', 800, 600, '看各种直播门户', controls)

    def start(self):
        super().start()

    def stop(self):
        self.stop_flag = True
        super().stop()

    def check_thread_func(self):
        last = 0
        while not self.stop_flag:
            time.sleep(0.1)
            if time.time() - last > 60.0 * 5: # check every 5 minitue
                last = time.time()
                print("thread loop")
                for fav in self.favs:
                    if self.stop_flag:
                        break
                    time.sleep(0.1)
                    print(f"check {fav['url']}")
                    real_url, site = self.get_real_url(fav['url'])
                    print(f"check ret {real_url}")
                    fav['online'] = '在线' if real_url else '离线'
                    self.favs = self.favs

    def danmu_thread_func(self, url):
        pass

    def create_damnu_client(self, url):
        ret, site = match(url)

        print(f'create_damnu_client {ret=} {site=}')

        if ret:
            danmu = site.get('danmu')
            if danmu:
                print(danmu)
                module_name, attr_name = danmu.rsplit('.', 1)
                module = importlib.import_module(f'..dmclient.{module_name}', package=__name__)
                Cls = getattr(module, attr_name)
                return Cls()
        return None

    def get_real_url(self, url):
        def call_get_real_url(module, ret):
            if hasattr(module, 'get_real_url'):
                return module.get_real_url(ret)
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj):
                    inst = obj(ret)
                    if hasattr(inst, 'get_real_url'):
                        return inst.get_real_url()
            return False

        ret, site = match(url)

        if ret:
            module_name = site['realurl']
            module = importlib.import_module(f'..real-url.{module_name}', package=__name__)
            try:
                real_url = call_get_real_url(module, ret)
                return real_url, site
            except Exception as e:
                import traceback
                traceback.print_exc()
        return None, None

    def play(self, url, caption, show_result=False):
        try:
            real_url, site = self.get_real_url(url)
            if not real_url:
                self.player and self.player.toast('main', '直播不存在或者未开播')
                return
            if 'key' in site:
                if callable(site['key']):
                    real_url = site['key'](real_url)
                else:
                    print(real_url)
                    real_url = real_url[site['key']]
            hasattr(self.player, "clearDanmu") and self.player.clearDanmu()
            try:
                self.player.play(real_url, caption=caption)
            except:
                self.player.play(real_url)
            
            self.real_url = real_url
            self.page_url = url

            if show_result:
                headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
                r = requests.get(url, headers = headers)
                if r.status_code == 200:
                    soup = bs(r.content, 'html.parser')
                    title = soup.find('title')
                    self.result = [{
                        'name': title.string,
                        'url': url,
                        'online': '在线'
                    }]
                    if self.player.setCaption : 
                        self.player.setCaption(title)
        except Exception as e:
            import traceback
            traceback.print_exc()

    def on_danmu(self, message):
        self.player.addDanmu(message)

    def on_play_click(self, *args):
        self.result = []
        url = self.q
        self.play(url, None, True)

    def on_play_fav_click(self, page, listControl, item, itemControl):
        url = self.favs[item]['url']
        name = self.favs[item]['name']
        self.play(url, name, False)

    def on_add_fav_click(self, page, listControl, item, itemControl):
        if self.result[0] not in self.favs:
            self.favs = self.favs + self.result
            self.result = []
            self.save_favs()

    def on_del_fav_click(self, page, listControl, item, itemControl):
        self.favs.pop(item)
        self.favs = self.favs
        self.save_favs()

    def on_toggle_danmu_click(self, *a):
        self.player.showDanmu(self.danmuShow)
        print(f'{a=}, {self.danmuShow=}')

    def save_favs(self):        
        f = open("favs.json", "w")
        favs = []
        for fav in self.favs:
            favs.append({
                'name': fav['name'],
                'url': fav['url']
            })
        f.write(json.dumps(favs, indent=4))
        f.close()

    def load_favs(self):
        try:
            with open("favs.json") as f:
                favs = json.loads(f.read())
                for fav in favs:
                    fav['online'] = '正在检测'
                self.favs = favs
        except FileNotFoundError:
            pass
    
           
def newPlugin(player:StellarPlayer.IStellarPlayer,*arg):
    plugin = MyPlugin(player)
    return plugin

def destroyPlugin(plugin:StellarPlayer.IStellarPlayerPlugin):
    plugin.stop()
