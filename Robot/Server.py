from SocketServer import ThreadingTCPServer, BaseRequestHandler
from rasa_nlu.model import Interpreter
from scripts.rasa_robot import Robot
from warnings import filterwarnings
from time import sleep
from sys import version_info

filterwarnings('ignore')

if version_info < (3, 0):
    MODEL_ADDR = './data2/models/current/nlu'
else:
    MODEL_ADDR = './data3/models/current/nlu'
    Interpreter = RasaNLUInterpreter('./models/nlu/default/weathernlu')
INTERPRETER = Interpreter.load(MODEL_ADDR)
HOST, PORT = "localhost", 8877

class MyTCPHandler(BaseRequestHandler):
    def handle(self):
        robot = Robot(self.request, INTERPRETER)
        while True:
            self.request.sendall('SESSIONSTOP')
            try:
                if not robot.session():
                    self.request.sendall('STOPRUNNING')
                    del robot
                    break
            except:
                self.request.sendall('There is something mistakes happended.')

if __name__ == "__main__":
    server = ThreadingTCPServer((HOST, PORT), MyTCPHandler)
    print 'Robot Server is running at (%s:%s)' % (HOST, PORT)
    server.serve_forever()
