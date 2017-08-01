# -*- coding:utf-8 -*-

import time
import requests
import re
import random


class Bot(object):
    def __init__(self,name,icon='bakyura-2x'):
        self.name = name
        self.icon = icon
        self.session = requests.session()

    def save_cookie(self,file_name):
        f = open(file_name,'w+')
        f.write(str(self.session.cookies.get_dict()))
        f.close()

    def load_cookie(self,file_name):
        f = open(file_name,'r')
        self.session.cookies.update(eval(f.read()))
        f.close()

    def leave_room(self):
        leave_body = {
            'leave': 'leave'
        }
        lr = self.session.post('https://drrr.com/room/?ajax=1', leave_body)
        lr.close()

    def new_host(self,new_host_id):
        new_host_body = {
            'new_host': new_host_id
        }
        nh = self.session.post('https://drrr.com/room/?ajax=1', new_host_body)
        nh.close()

    def post(self,message, url='', to=''):
        post_body = {
            'message': message,
            'url': url,
            'to': to
        }
        p = self.session.post(url='https://drrr.com/room/?ajax=1', data=post_body)
        p.close()

    def login(self):
        home = self.session.get('https://drrr.com')
        token = re.search('<input type="hidden" name="token" data-value=".*?">', home.text).group(0)[-34:-2]
        home.close()
        login_body = {
            'name': self.name,
            'login': 'ENTER',
            'token': token,
            'direct-join': '',
            'language': 'zh-CN',
            'icon': self.icon
        }
        li = self.session.post('https://drrr.com', login_body)
        li.close()

    def room_enter(self,url_room):
        re = self.session.get(url_room)
        re.close()
        room = self.session.get('https://drrr.com/json.php?fast=1')
        #talks = re.findall('{"id".*?"message":".*?"}', re.search('"talks":.*', room).group(0))
        return room.text

    def room_update(self,room_text):
        update = re.search('"update":\d+.\d+', room_text).group(0)[9:]
        url_room_update = 'https://drrr.com/json.php?update=' + update
        while 1:
            time.sleep(3)
            ru = self.session.get(url_room_update)
            update = re.search('"update":\d+.\d+', ru.text).group(0)[9:]
            url_room_update = 'https://drrr.com/json.php?update=' + update
            if 'talks' in ru.text:
                talks_update = re.findall('{"id".*?"message":".*?"}', re.search('"talks":.*', ru.text).group(0))
                for tu in talks_update:
                    message = re.search('"message":".*?"', tu).group(0)[11:-1].decode('unicode_escape')
                    if '!leave' in message:
                        list_id = re.findall('"id":".*?"', tu)
                        if len(list_id) > 2:
                            self.leave_room()
                            return 'leave'
                    elif '!room sd' in message:
                        list_id = re.findall('"id":".*?"', tu)
                        if len(list_id) > 2:
                            new_hosts_id = list_id[2][6:-1]
                            self.new_host(new_host_id=new_hosts_id)
            if '"type":"join"' in ru.text:
                self.post('/me 歡迎光臨，輕食咖啡館')
            ru.close()

    def give_time(self):
        while 1:
            if time.time() % 600 < 5:
                try:
                    give_time = time.strftime('現在是中原標準時間 %Y年%m月%d日 %H時%M分',time.localtime(time.time()))
                    self.post('/me %s' % give_time)
                    time.sleep(580)
                except:
                    print '[Err] Give time error at %s' % time.strftime('%Y/%m/%d %H:%M:%S',time.localtime(time.time()))

    def tips(self):
        while 1:
            time.sleep(7200 * random.random())
            if 0 < int(time.strftime('%H',time.localtime(time.time()))) < 6:
                list_tips = ['/me 寂静的深夜，除了自己的心跳，还有我在陪你',
                             '/me 夜都睡了，你还不睡吗？',
                             '/me 晚安，月亮也一起睡了',
                             '/me 夜深了，天上的星星都已经睡了',
                             '/me 晚睡伤身体，客官早点歇息吧',
                             '/me 深夜了，不知道有多少人和你一样还没有睡呢？',
                             '/me 夜深了，来日方长，早点休息',
                             '/me 不要活得太累，不要忙得太疲惫',
                             '/me 愿与您分享这夜色，早点休息',
                             '/me 还在熬夜的您，让我为您点一盏灯',
                             '/me 今夜微风轻送，伴你入美梦',
                             '/me 周末也要早点休息，晚安地球人',
                             '/me 夜深了，常常熬夜可不好哦'
                ]
                list_tips_index = int(13 * random.random())
                self.post(list_tips[list_tips_index])