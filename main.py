# -*- coding:utf-8 -*-

import drrrobot
import os
import threading
import time

name = 'にじ'
icon = 'bakyura-2x'
file_name = 'niji.cookie'
url_room = raw_input('Input the [Room URL] ')

niji = drrrobot.Bot(name=name,icon=icon)

while 1:
    try:
        if not os.path.isfile(file_name):
            niji.login()
            niji.save_cookie(file_name=file_name)
            room = niji.room_enter(url_room=url_room)
            t_tips = threading.Thread(target=niji.tips)
            t_tips.start()
            niji.room_update(room_text=room)
        else:
            niji.load_cookie(file_name=file_name)
            room = niji.room_enter(url_room=url_room)
            t_tips = threading.Thread(target=niji.tips)
            t_tips.start()
            niji.room_update(room_text=room)
        time.sleep(10)
    except:
        print '[Err] connection error'