# coding: utf-8
import itchat
from scripts.client import BaseClient
from scripts.translater import translate, check_language
from Queue import Queue

PORT, HOST = 8877, 'localhost'
CHINESE, ENGLISH = 1, 2
Clients = {}

class WxClient(BaseClient):
    def __init__(self, **kward):
        BaseClient.__init__(self, **kward)
        self._queue = Queue(2)
        self._language = kward['Language']
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
        print 'Robot:', receive.decode('utf-8')
        if self._language != 2 and 'link' not in receive:
            receive = translate(receive)
        itchat.send('BOT:'+receive.decode('utf-8'), self._ID)

    def call(self):
        msg = self._queue.get()
        print 'Client:', msg
        return msg

@itchat.msg_register(itchat.content.TEXT)
def reply_text(msg):
    name, message = msg['FromUserName'], msg['Content']

    lang = check_language(message)
    if lang != ENGLISH:
        message = translate(message)

    if name in Clients and Clients[name].is_alive():
        if lang != Clients[name].language:
            Clients[name].language = lang
        Clients[name].queue.put(message)
        
    elif 'bot' in message.lower():
        Clients[name] = WxClient(HOST=HOST, PORT=PORT, Language=lang, ID=name)
        Clients[name].callback('I am here!')

if __name__ == '__main__':
    itchat.auto_login(hotReload=True)
    itchat.run()
