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
        print 'Client:', receive
        if self._language != 2:
            receive = translate(receive)
        itchat.send_msg(u'BOT:' + receive.decode('utf-8'), toUserName=self._user)

    def call(self):
        msg = self._queue.get()
        print 'Robot:', msg
        return msg

@itchat.msg_register(TEXT)
def reply_my_friend(msg):
    name, message = msg['FromUserName'], msg['Text']

    L = check_language(message)
    if (name not in Pipes) or not Clients[name].is_alive():
        q = Queue(1)
        Pipes[name] = q
        c = WxClient(HOST=HOST, PORT=PORT, Language=L,
                 User=name, Queue=q)
        c.start()
        Clients[name] = c
        
    if L != ENGLISH:
        message = translate(message)
    if L != Clients[name]._language:
        Clients[name]._language = L
    Pipes[name].put(message)
    
itchat.auto_login(hotReload=True)
itchat.run()
