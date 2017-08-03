# -*- coding:utf-8 -*-

import time
import requests
import re
import random


class Song(object):
    def __init__(self,keyword):
        self.keyword = keyword
        self.url_song = None
        self.name_song = None
        self.artist_song = None

    def qq_search(self):
        search = requests.get('http://s.music.qq.com/fcgi-bin/music_search_new_platform?t=0&n=1&aggr=1&cr=1&loginUin=0&format=json&inCharset=utf-8&outCharset=utf-8&notice=0&platform=jqminiframe.json&needNewCode=0&p=1&catZhida=0&remoteplace=sizer.newclient.next_song&w=%s' % requests.utils.quote(self.keyword))
        resp_search = re.findall('f":"\d+\|.*?\|\d+\|.*?\|', search.text)
        if resp_search:
            info_song = resp_search[0]
            url_song = 'http://ws.stream.qqmusic.qq.com/%s.m4a?fromtag=46' % re.findall('"\d+', info_song)[0][1:]
            name_song = re.findall('\d\|.*?\|', info_song)[0][2:-1]
            artist_song = re.findall('\d\|.*?\|', info_song)[1][2:-1]
            self.url_song = url_song
            self.name_song = name_song
            self.artist_song = artist_song
            return True
        else:
            return False


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

    def post(self, message, url='', to=''):
        post_body = {
            'message': message,
            'url': url,
            'to': to
        }
        p = self.session.post(url='https://drrr.com/room/?ajax=1', data=post_body)
        p.close()

    def share_music(self, url, name=''):
        share_music_body = {
            'music': 'music',
            'name': name,
            'url': url
        }
        p = self.session.post(url='https://drrr.com/room/?ajax=1', data=share_music_body)
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
                    message = re.search('"message":".*?"', tu).group(0)[11:-1].decode('unicode_escape').encode('utf-8')
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
                    elif '!m' in message:
                        if re.findall('!m .*',message):
                            keyword = re.findall('!m .*',message)[0][3:]
                            song = Song(keyword=keyword)
                            search_resp = song.qq_search()
                            if search_resp:
                                self.share_music(url=song.url_song,name='%s - %s' % (song.name_song,song.artist_song))
                            else:
                                self.post('穩唔到啊，自己聽罷啦')
                    elif '!feedback' in message:
                        if re.findall('!feedback .*',message):
                            feedback = re.findall('!feedback .*',message)[0][10:]
                            f = open('%s.feedback'% time.time(),'w+')
                            f.write(feedback)
                            f.close()
                    elif '@にじ' in message:
                        self.post('都唔知你up乜柒')
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
            time.sleep(5400 * random.random())
            if 0 < int(time.strftime('%H',time.localtime(time.time()))) < 6:
                list_tips = ['寂靜的深夜，除了自己的心跳，還有我在陪妳',
                             '夜都睡了，妳還不睡嗎？',
                             '晚安，月亮也壹起睡了',
                             '夜深了，天上的星星都已經睡了',
                             '晚睡傷身體，客官早點歇息吧',
                             '深夜了，不知道有多少人和妳壹樣還沒有睡呢？',
                             '夜深了，來日方長，早點休息',
                             '不要活得太累，不要忙得太疲憊',
                             '願與您分享這夜色，早點休息',
                             '還在熬夜的您，讓我為您點壹盞燈',
                             '今夜微風輕送，伴妳入美夢',
                             '周末也要早點休息，晚安地球人',
                             '夜深了，常常熬夜可不好哦'
                ]
                list_tips_index = int(13 * random.random())
                self.post(list_tips[list_tips_index])