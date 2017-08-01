# -*- coding:utf-8 -*-

import drrrobot
import os
import threading
import time

name = 'にじ#niji1997'
icon = 'bakyura-2x'
file_name = 'niji.cookie'
url_room = raw_input('Input the [Room URL] ')

niji = drrrobot.Bot(name=name,icon=icon)

t_give_time = threading.Thread(target=niji.give_time)
t_give_time.start()

t_tips = threading.Thread(target=niji.tips)
t_tips.start()

while 1:
    try:
        if not os.path.isfile(file_name):
            niji.login()
            niji.save_cookie(file_name=file_name)
            room = niji.room_enter(url_room=url_room)
            leave = niji.room_update(room_text=room)
            if leave == 'leave':
                break
        else:
            niji.load_cookie(file_name=file_name)
            room = niji.room_enter(url_room=url_room)
            leave = niji.room_update(room_text=room)
            if leave == 'leave':
                break
        time.sleep(10)
    except:
        print '[Err] Room update error at %s' % time.strftime('%Y/%m/%d %H:%M:%S',time.localtime(time.time()))