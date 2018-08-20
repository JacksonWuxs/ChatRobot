from wxpy import *
from client import Client
from time import localtime
from Queue import Queue

PORT, HOST = 8877, 'localhost'

class WxClient(Client):
    def __init__(self, **kward):
        Client.__init__(self, **kward)
        self._user = kward['User']
        self._queue = kward['Queue']
        
    def callback(self, receive):
        '''Rewrite this function for different API
        '''
        self._user.send(receive)

    def call(self):
        return text

Pipes = {}
bot = Bot(cache_path=True)
bot.file_helper.send(str(localtime()))

@bot.register(except_self=False)
def reply_my_friend(msg):
    name = msg.nickname
    print '%s : %s' % (name, msg.text)
    if name not in clients:
        q = Queue(1)
        Pipes[name] = q
        client = WxClient(HOST=HOST, PORT=PORT, User=name, Queue=q)
        client.start()
    Pipes[name].put(msg.text)
    return

embed(shell='python')
