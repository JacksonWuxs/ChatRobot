# -*- coding: utf-8 -*-
import itchat
from itchat.content import *
from scripts.client import Client
from scripts.translater import translate, check_language
from Queue import Queue

PORT, HOST = 8877, 'localhost'
CHINESE, ENGLISH = 1, 2
Pipes, Clients = {}, {}

class WxClient(Client):
    def __init__(self, **kward):
        Client.__init__(self, **kward)
        self._user = kward['User']
        self._queue = kward['Queue']
        self._language = kward['Language']

    def callback(self, receive):
        if check_language != self._language:
            receive = translate(receive).encode('utf-8')
        itchat.send_msg(receive.decode('utf-8'), toUserName=self._user)

    def call(self):
        return self._queue.get()

@itchat.msg_register(TEXT)
def reply_my_friend(msg):
    name, message = msg['FromUserName'], translate(msg['Text'])

    if (name not in Pipes) or not Clients[name].is_alive():
        q = Queue(1)
        Pipes[name] = q
        c = WxClient(HOST=HOST, PORT=PORT, Language=check_language(message),
                 User=name, Queue=q)
        c.start()
        Clients[name] = c

    if check_language(message) != ENGLISH:
        message = translate(message)
    Pipes[name].put(message)
    
itchat.auto_login(hotReload=True)
itchat.run()
