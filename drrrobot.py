# -*- coding:utf-8 -*-

import time
import requests
import re


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
                            quit()
                    elif '!room sd' in message:
                        list_id = re.findall('"id":".*?"', tu)
                        if len(list_id) > 2:
                            new_hosts_id = list_id[2][6:-1]
                            self.new_host(new_host_id=new_hosts_id)
            if '"type":"join"' in ru.text:
                self.post('/me 歡迎光臨，輕食咖啡館')
            ru.close()

    def tips(self):
        while 1:
            self.post('/me 歡迎光臨，輕食咖啡館')
            time.sleep(1200)