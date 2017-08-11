# -*- coding:utf-8 -*-

import time
import requests
import HTMLParser
import re
import random
import threading
import smtplib
import email
from email.mime.text import MIMEText

global ts_last_greeting
ts_last_greeting = 0


class Song(object):
    def __init__(self,keyword):
        self.keyword = keyword
        self.url_song = None
        self.name_song = None
        self.artist_song = None

    # search in qq music library
    def qq_search(self):
        search = requests.get('http://s.music.qq.com/fcgi-bin/music_search_new_platform?t=0&n=1&aggr=1&cr=1&loginUin=0&format=json&inCharset=utf-8&outCharset=utf-8&notice=0&platform=jqminiframe.json&needNewCode=0&p=1&catZhida=0&remoteplace=sizer.newclient.next_song&w=%s' % requests.utils.quote(self.keyword))
        resp_search = re.findall('f":"\d+\|.*?\|\d+\|.*?\|', search.text)
        if resp_search:
            info_song = resp_search[0]
            list_name_artist = re.findall('\d\|.*?\|', resp_search[0])
            self.url_song = 'http://ws.stream.qqmusic.qq.com/%s.m4a?fromtag=46' % re.findall('"\d+', info_song)[0][1:]
            try:
                self.name_song = HTMLParser.HTMLParser().unescape(list_name_artist[0][2:-1].replace('&amp;','&'))
            except:
                self.name_song = list_name_artist[0][2:-1]
            try:
                self.artist_song = HTMLParser.HTMLParser().unescape(list_name_artist[1][2:-1].replace('&amp;','&'))
            except:
                self.artist_song = list_name_artist[1][2:-1]
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
        global ts_last_greeting        
        # update timestamp
        update = re.search('"update":\d+.\d+', room_text).group(0)[9:]
        # room update request url
        url_room_update = 'https://drrr.com/json.php?update=' + update
        while 1:
            time.sleep(1)
            ru = self.session.get(url_room_update)
            update = re.search('"update":\d+.\d+', ru.text).group(0)[9:]
            url_room_update = 'https://drrr.com/json.php?update=' + update
            # search "talks" block in room update response
            if 'talks' in ru.text:
                talks_update = re.findall('{"id".*?"message":".*?"}', re.search('"talks":.*', ru.text).group(0))
                # talk in "talks" block
                for tu in talks_update:
                    message = re.search('"message":".*?"', tu).group(0)[11:-1].decode('unicode_escape').encode('utf-8')
                    if ('/' in message or '@' in message):
                        # search "from" block
                        info_sender = re.findall('"from":{.*?}', tu)
                        if info_sender:
                            info_sender = info_sender[0]
                            name_sender = re.findall('"name":".*?"', info_sender)[0][8:-1].decode('unicode_escape')
                            if name_sender == u'にじ':
                                continue
                            id_sender = re.findall('"id":".*?"', info_sender)[0][6:-1]
                            # search "to" block in html
                            info_receiver = re.findall('"to":{.*?}', tu)
                            if info_receiver:
                                #info_receiver = info_receiver[0].decode('unicode_escape').encode('utf-8')
                                is_leave = self.handle_private_message(message=message,id_sender=id_sender,name_sender=name_sender)
                                if is_leave:
                                    return True
                            else:
                                self.handle_message(message=message,name_sender=name_sender)
                    elif ('好' in message or '安' in message):
                        global ts_last_greeting
                        if time.time() - ts_last_greeting > 60:
                            ts_last_greeting = time.time()                        
                            # search "from" block
                            info_sender = re.findall('"from":{.*?}', tu)
                            if info_sender:
                                info_sender = info_sender[0]
                                name_sender = re.findall('"name":".*?"', info_sender)[0][8:-1].decode('unicode_escape')
                                if name_sender == u'にじ':
                                    continue                        
                                self.reply_greeting(message)
            if '"type":"join"' in ru.text:
                self.post('/me 歡迎光臨，輕食咖啡館')
            ru.close()

    def give_time(self):
        while 1:
            timestamp = time.time()
            hour = int(time.strftime('%H',time.localtime(time.time())))
            if 8 < hour < 24:
                if timestamp % 600 < 5:
                    give_time = time.strftime('現在是中原標準時間 %Y年%m月%d日 %H時%M分', time.localtime(time.time()))
                    self.post('/me %s' % give_time)
                    time.sleep(590)
            else:
                if timestamp % 1800 < 5:
                    give_time = time.strftime('現在是中原標準時間 %Y年%m月%d日 %H時%M分', time.localtime(time.time()))
                    self.post('/me %s' % give_time)
                    time.sleep(1790)

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
                             '工作也要早點休息，晚安地球人',
                             '夜深了，常常熬夜可不好哦'
                ]
                list_tips_index = int(13 * random.random())
                self.post(list_tips[list_tips_index])

    def feedback(self,message,name_sender,to=''):
        if re.findall('/feedback .*', message):
            text_feedback = name_sender.encode('utf-8') + '： ' +  re.findall('/feedback .*', message)[0][10:]
            try:
                mail = MIMEText(text_feedback, 'plain', 'utf-8')
                mail['Subject'] = '使用者反馈'
                mail['From'] = email.utils.formataddr(['にじ', 'niji_drrrobot@126.com'])
                mail['To'] = email.utils.formataddr(['時光會凝聚嗎', 'willtimecondense@qq.com'])
                server = smtplib.SMTP(host='smtp.126.com', port=25)
                server.login(user='niji_drrrobot@126.com', password='nijiniji1997')
                server.sendmail(from_addr='niji_drrrobot@126.com', to_addrs='willtimecondense@qq.com',msg=mail.as_string())
                server.quit()
                self.post(message='反饋成功。如有需要可追加發送你的聯繫方式，感謝關注',to=to)
            except:
                self.post(message='反饋失敗，請稍後重試',to=to)
        else:
            self.post(message='喪失好好說話的能力了？ /feedback + 空格 + 建議', to=to)

    def help(self,to=''):
        self.post(message='本萌妹的指令詳見鏈接',url='https://drrr.wiki/%E8%BC%95%E9%A3%9F%E5%92%96%E5%95%A1%E9%A4%A8#BOT',to=to)

    def music(self,message,name_sender,to=''):
        if re.findall('/m .*', message):
            keyword = re.findall('/m .*', message)[0][3:]
            song = Song(keyword=keyword)
            search_resp = song.qq_search()
            if search_resp:
                self.share_music(url=song.url_song, name='%s - %s by @%s' % (song.name_song, song.artist_song, name_sender))
            else:
                self.post(message='找不到這首歌啊，點別的吧', to=to)
        else:
            self.post(message='喪失好好說話的能力了？ /m + 空格 + 歌曲', to=to)

    def handle_message(self,message,name_sender):
        if '/m' in message:
            t_music = threading.Thread(target=self.music,args=(message,name_sender))
            t_music.start()
        elif '/help' in message:
            t_help = threading.Thread(target=self.help)
            t_help.start()
        elif '/feedback' in message:
            t_feedback = threading.Thread(target=self.feedback,args=(message,name_sender))
            t_feedback.start()
        elif '@にじ' in message:
            t_help = threading.Thread(target=self.help)
            t_help.start()

    def handle_private_message(self,message,id_sender,name_sender):
        if '/niji leave' in message:
            self.leave_room()
            return True
        elif '/niji room' in message:
            self.new_host(new_host_id=id_sender)
        elif '/m' in message:
            t_music = threading.Thread(target=self.music, args=(message,name_sender,id_sender))
            t_music.start()
        elif '/help' in message:
            t_help = threading.Thread(target=self.help,args=(id_sender,))
            t_help.start()
        elif '/feedback' in message:
            t_feedback = threading.Thread(target=self.feedback,args=(message,name_sender,id_sender))
            t_feedback.start()
        elif '@にじ' in message:
            t_help = threading.Thread(target=self.help,args=(id_sender,))
            t_help.start()
        return False
    
    def reply_greeting(self,message):
        if ('早上好' in message or '早安' in message):
            self.post('早安')
        elif '中午好' in message:
            self.post('中午好')
        elif '下午好' in message:
            self.post('下午好')
        elif ('晚上好' in message or '晚好' in message):
            self.post('晚上好')
        elif '晚安' in message:
            self.post('晚安')