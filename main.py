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

DEFAULT_IMAGE = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAQMAAADCCAMAAAB6zFdcAAAAQlBMVEX///+hoaGenp6ampr39/fHx8fOzs7j4+P8/Pyvr6/d3d3FxcX29va6urqYmJjs7OzU1NSlpaW1tbWtra3n5+e/v78TS0zBAAACkUlEQVR4nO3b63KCMBCGYUwUUVEO6v3fagWVY4LYZMbZnff51xaZ5jON7CZNEgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABQb5tvI8qzX4/nH84XG5Upfj2ir2V2E5fZ/XpIX9saMnhkYLIkiyRJjdgMoiEDMmiQgfwM8rSu77ew2wnPoLTmwdZBs0J2BuXrYckcQm4nOoP+WcmWAbcTnUHZPy9eA24nOoN7n0HI54ToDM5k8PjluwyqgNuJzqDoaugPg8gWZ4noDAYLwuIg75fLeeHHsjNIzrZJwWwW+0DNsmEWPjiEZ5AcD8ZUu8VZ8HyQMifvBdIz+PS33i8adu+7Qn4Gn1Tdupl7rlCfQb9seosK7RkcBy1o30iVZ5CPOtDW3WhQnsF13IV3v0p3BqfJRoSpXVepzmA/24+yqeMyzRm4tqOs44lSUwa3yfgOri25av5CPRnklR33VlPnrqSZV09qMsiqSWV082xOz1uPajJ49pTM/f115k6guWa6JGjJ4N1lt8fXN2rv/vysjFaSQdFXBc/KKF04ptFPliclGVR9Bu27XCyeVOkmy5OODAZN9rYyyip/AIPJ8qIig+PoXbf7YdPdncFoSdCQQT4ZceV+MhiFMBy0hgyu0yGvOLI17KwpyGBaHK5jtt0N5GcwLw7XZdB31sRn8O+ziqYro8Vn4CwOV+k6a9Iz+PwRsKC7h+gMfMXhKu/OmuwM/MXhKq8yWnYG/uJw5Uxoy2jRGZTBZ/jboxuSM1guDtdNhKazJjiDbNMe0AxzKUVnkO+jEJxBxNtJzWCTxlNLzSB8KehJ/H+mJGYAjaDjzj9SnHZRuXZiAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAECXP1XDHv7U4SNFAAAAAElFTkSuQmCC'


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
                if self.player.getSnapshot:
                    time.sleep(2.0)
                    image = self.player.getSnapshot({'width': 100, 'height': 100})
                    for item in self.result:
                        if item['url'] == self.page_url:
                            item['image'] = 'data:image/png;base64,' + image
                            self.result = self.result
                            break
                    for item in self.favs:
                        if item['url'] == self.page_url:
                            print(f'update image {self.page_url}')
                            item['image'] = 'data:image/png;base64,' + image
                            self.favs = self.favs
                            self.save_favs()
                            break
                
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
                {'type':'image', 'name':'image', 'width':120},
                {'type':'space','width':10},
                {
                    'group': [
                        {'type':'label','name':'name'},
                        {'type':'link','name':'url', 'height':20},
                        {'type':'link','name':'收藏','width':50, '@click': 'on_add_fav_click'},
                    ],
                    'dir':'vertical',
                }
            ]
        ]
        favs_layout = [            
            [   
                {'type':'image', 'name':'image', 'width':120},
                {'type':'space','width':10},
                {
                   'group': [
                        {'type':'label','name':'name', 'height':20},
                        {'type':'link','name':'url', 'height':20},
                        {'type':'label', 'name':'online', 'height':20, 'matchParent':True},
                        {
                            'group': [
                                {'type':'link','name':'播放','width':50, 'matchParent':True, '@click': 'on_play_fav_click'},
                                {'type':'link','name':'删除','width':50, 'matchParent':True, '@click': 'on_del_fav_click'},
                            ]
                        },
                        # {'group':
                        #     [
                        #         {'type':'button','name':'删除','width':60,'matchParent':True, '@click':'on_list_del_click'},
                        #         {'type':'button','name':'删除2','width':60,'matchParent':True, '@click':'on_list_del_click'},
                        #         {'type':'button','name':'删除3','width':60,'matchParent':True, '@click':'on_list_del_click'},
                        #     ]
                        # },
                    ],
                    'dir':'vertical',
                }
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
                            {'type':'list','name':'result', 'height': 80, 'itemheight':80, 'itemlayout': result_layout, ':value': 'result','marginSize':5},
                            {'type':'space', 'height':10 },   
                            {'type':'label','name': '收藏列表', 'height':30},  
                            {'type':'list','name':'favs', 'itemheight':80, 'itemlayout': favs_layout, ':value': 'favs','marginSize':5, 'separator': True},                              
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
            print(f'get real url : {module_name}')
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
            headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36', 'referer': url}
            try:
                self.player.play(real_url, caption=caption, headers=headers)
            except:
                self.player.play(real_url, headers=headers)
            
            self.real_url = real_url
            self.page_url = url

            if show_result:
                headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
                r = requests.get(url, headers = headers)
                if r.status_code == 200:
                    soup = bs(r.content, 'html.parser')
                    title = soup.find('title')
                    self.result = [{
                        'name': title.string[:30],
                        'url': url,
                        'online': '在线',
                        'image': DEFAULT_IMAGE
                    }]
                    if self.player.setCaption : 
                        self.player.setCaption(title.string)
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
        if len(self.result) == 0: return
        url = self.result[0]['url']

        if len(list(filter(lambda x: x['url'] == url, self.favs))) == 0:
            self.favs = self.result + self.favs
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
                'url': fav['url'],
                'image': fav['image']
            })
        f.write(json.dumps(favs, indent=4))
        f.close()

    def load_favs(self):
        try:
            with open("favs.json") as f:
                favs = json.loads(f.read())
                for fav in favs:
                    fav['online'] = '正在检测'
                    if 'image' not in fav:
                        fav['image'] = DEFAULT_IMAGE
                self.favs = favs
        except FileNotFoundError:
            pass
    
           
def newPlugin(player:StellarPlayer.IStellarPlayer,*arg):
    plugin = MyPlugin(player)
    return plugin

def destroyPlugin(plugin:StellarPlayer.IStellarPlayerPlugin):
    plugin.stop()
