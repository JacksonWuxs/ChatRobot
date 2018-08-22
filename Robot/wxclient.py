# coding: utf-8
import itchat
from itchat.content import *
from scripts.client import Client
from scripts.translater import translate, check_language
from Queue import Queue

PORT, HOST = 8877, 'localhost'
CHINESE, ENGLISH = 1, 2
Clients = {}
MyID = ''

class WxClient(Client):
    def __init__(self, **kward):
        Client.__init__(self, **kward)
        self._queue = Queue(1)
        self._language = kward['Language']
        if self._ID == MyID:
            self._ID = 'filehelper'
        self.start()

    @property
    def language(self):
        return self._language

    @language.setter
    def language(self, l):
        self._language = l

    @property
    def queue(self):
        return self._queue

    def callback(self, receive):
        print 'Client:', receive
        if self._language != 2 and 'link' not in receive:
            receive = translate(receive)
        itchat.send_msg(u'BOT:'+receive.decode('utf-8'), toUserName=self._ID)

    def call(self):
        msg = self._queue.get()
        print 'Robot:', msg
        return msg

@itchat.msg_register(TEXT)
def reply_my_friend(msg):
    name, message = msg['FromUserName'], msg['Text']
        
    lang = check_language(message)
    if lang != ENGLISH:
        message = translate(message)
        
    if name in Clients and Clients[name].is_alive():
        if lang != Clients[name].language:
            Clients[name].language = lang
        Clients[name].queue.put(message)
    elif msg['MsgType'] == '51':
        My_ID = name
        
    if 'robot' in message.lower() or '机器人' in message:
        Clients[name] = WxClient(HOST=HOST, PORT=PORT, Language=lang,
                                 ID=name)
        Clients[name].callback('I am here! Talk to me!')
        Clients[My_ID].callback('Talking to %s' % msg['RecommendInfo'])

@itchat.msg_register(TEXT, isGroupChat=True)
def reply_At_group(msg):
    if not msg.isAt:
        return
    return 'The stock market AI Assistant is online! please click on the avatar to talk to me privately.'
    
    
itchat.auto_login(hotReload=True)
itchat.run()
