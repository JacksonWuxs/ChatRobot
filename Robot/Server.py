from SocketServer import ThreadingTCPServer, BaseRequestHandler
from rasa_nlu.model import Interpreter
from rasa_robot import Robot
from warnings import filterwarnings
from time import sleep

filterwarnings('ignore')
HOST, PORT = "localhost", 8877
MODEL_ADDR = './models/current/nlu'
INTERPRETER = Interpreter.load(MODEL_ADDR)

class MyTCPHandler(BaseRequestHandler):
    def handle(self):
        robot = Robot(self.request, INTERPRETER)
        while True:
            sleep(1)
            self.request.sendall('SESSIONSTOP')
            if not robot.session():
                break

if __name__ == "__main__":
    server = ThreadingTCPServer((HOST, PORT), MyTCPHandler)
    print 'I am starting to offer service!'
    server.serve_forever()
