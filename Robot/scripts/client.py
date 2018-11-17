# coding: utf-8
from socket import socket, AF_INET, SOCK_STREAM
from random import randint
from threading import Thread

HOST, PORT = "localhost", 8877
ID = str(randint(1000,9999))

class BaseClient(Thread):
    def __init__(self, **kward):
        Thread.__init__(self)
        self._HOST = kward.get('HOST', 'localhost')
        self._PORT = kward.get('PORT', 8879)
        self._ID = kward.get('ID', str(randint(1000, 9999)))
        self._conn = socket(AF_INET, SOCK_STREAM)
        self._conn.connect((self._HOST, self._PORT))
        self._running = True

    def run(self):
        GET_INFO = self.listen()
        try:
            while self._running:
                if GET_INFO:
                    self.say()
                GET_INFO = self.listen()
                
        except Exception, e:
            print('Something wrong as %s' % e)
            
        finally:
            self._conn.close()
                
    def say(self):
        data = self.call()
        self._conn.sendall(data)

    def listen(self):
        receive = self._conn.recv(1024).strip().decode('utf-8')
        if u'STOPRUNNING' in receive:
            self._running = False
            return
            
        elif u'SESSIONSTOP' in receive:
            receive.replace(u'SESSIONSTOP', u'')
            print('')
            return True
            
        elif u'INPUT' in receive:
            receive.replace(u'INPUT', '')
            return True

        else:
            self.callback(receive.encode('utf-8'))
            return False

    def callback(self, receive):
        '''Rewrite this function for different API
        '''
        print(receive)

    def call(self):
        '''Rewrite this function for different API
        '''
        return input('YOU: ')

if __name__ == '__main__':
    user = BaseClient(HOST=HOST, PORT=PORT)
    user.start()
    user.join()
