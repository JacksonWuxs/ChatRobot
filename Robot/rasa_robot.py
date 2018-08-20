# coding: utf-8
from rasa_nlu.model import Interpreter
from random import choice
from time import localtime, sleep
from requests import get
from bs4 import BeautifulSoup
from collections import namedtuple
import sqlite3 as sql

STOCK_ADDR = 'http://hq.sinajs.cn/list=%s%s'
STOCK_FORMAT = ['Name', 'Open', 'High', 'Low', 'Current', 'volume']
NEWS_ADDR = 'http://search.sina.com.cn/?q=%s&range=all&c=news&sort=time'
NEWS_FORMAT = namedtuple('news', ['Keyword', 'Title', 'Link'])

RESPONSE_GREET = ['Hello, how are you?', 'Good to see you!', 'What can I do for you sir?', 'Nice to meet you.']
RESPONSE_THANKYOU = ['That is my honor to service you.', 'You are so kind.', 'You are welcome!']
RESPONSE_GOODBYE = ['See you!', 'See you next time!', 'I will be here all the time']
RESPONSE_GREAT_AFFIRM = ['OK, I will follow your command.']
RESPONSE_DENY_UNHAPPY = ['OK, I will not to do that.']

class Robot:
    def __init__(self, conn, interpreter):
        self._conn = conn
        self._interpreter = interpreter

    def session(self):
        '''The robot will do a entire operation in a session.
        '''
        
        intent = self.listen()
        if intent['intent'] == u'greet':
            self.response(choice(RESPONSE_GREET))

        elif intent['intent'] == u'thankyou':
            self.response(choice(RESPONSE_THANKYOU))
            return False

        elif intent['intent'] == u'goodbye':
            self.response(choice(RESPONSE_GOODBYE))
            return False

        elif intent['intent'] == u'search_stock':
            stock, subject = intent.get('stock', None), intent.get('subject', None)
            if stock and subject:
                self.response('I am searching for %s, please wait...' % stock)
            elif stock and not subject:
                subject = self.ask('What information you want to know about %s, price, news or others?' % stock.upper(), False)
            elif not stock and subject:
                stock = self.ask("Which company's %s you want to know?" % subject, False)
            else:
                self.response("Sorry, I didn't hear clear.")
                stock = self.ask('So, which company you want to know?', False)
                subject = self.ask('And, you want to know about ...', False)

            if subject in (u'news', 'new', 'info', 'information'):
                self.do_news(news=None, i=0, key=stock)
            else:
                self.do_stock(stock, subject)

        elif intent['intent'] == u'search_news':
            key = intent.get('key', None)
            while not key:
                key = self.ask("I didn't here clear, please tell me again what you want to know?", False)
            self.do_news(news=None, i=0, key=key)

        elif intent['intent'] == u'search_market':
            self.do_market(intent.get('country', None))

        elif intent['intent'] == u'help':
           self.response('I can search the latest stock market information for you.')

        else:
            self.response("I hear you, but I can't understand what you said.")
        return True
            
    def listen(self):
        '''Get the information from the client and parse the result
        '''
        ID, MSG = self._conn.recv(1024).strip().decode('utf-8').split(':')
        print '%s say: %s' % (ID, MSG)

        parse = self._interpreter.parse(MSG)
        obj = {'intent':parse[u'intent'][u'name']}
        if obj['intent'] == u'search_stock':
            for ent in parse[u'entities']:
                if ent.get(u'entity') == 'stock':
                    obj['stock'] = ent[u'value'].encode('utf-8')
                elif ent.get(u'entity') == 'subject':
                    obj['subject'] = ent[u'value'].encode('utf-8')
                    
        elif obj['intent'] == u'search_news':
            for ent in parse[u'entities']:
                if ent.get(u'entity') == 'key':
                    obj['key'] = ent[u'value'].encode('utf-8')
                    
        elif obj['intent'] == u'search_market':
            for ent in parse[u'entities']:
                if ent.get(u'entity') == 'country':
                    obj['country'] = ent[u'value'].encode('utf-8')

        return obj

    def response(self, msg):
        '''Format the message to response
        '''
        if isinstance(msg, list):
            msg = '\n'.join([every.encode('utf-8') for every in msg if every])
        self._conn.sendall('BOT: %s\n' % msg)

    def ask(self, msg, parse=True):
        '''Get more information from the client in one session.
        '''
        self.response(msg)
        sleep(1)
        self.response('INPUT')
        if parse:
            return self.listen()
        return self._conn.recv(1024).strip().split(':')[1]
    
    def do_market(self, market):
        if market is None:
            market = self.ask('Which market do you prefer, US or China?', False).upper()
            self.do_market(market)
        elif market in ('US', 'U.S', 'U.S.', 'AMERICAN', 'UNITED STATE'):
            _nas = self.get_stock('nasdaq')
            _sp = self.get_stock('biaopu')
            _djz = self.get_stock('djz')
            self.response('纳斯达克：%s | 标普500：%s | 道琼斯：%s' % (_nas, _sp, _djz))
        elif market in ('CHINA', 'CHINESE', 'CHIAN'):
            _shanghai = self.get_stock('shanghai')
            _shenzheng = self.get_stock('shenzheng')
            self.response('上证指数：%s | 深证指数：%s' % (_shanghai, _shenzheng))
        else:
            self.response('Sorry, we can not support %s market now.' % market)
            
    def do_stock(self, stock, subject):
        if subject.lower() == 'price':
            intent = self.ask('Do you mean the current price?')['intent']
            if intent in (u'mood_deny', u'mood_unhappy'):
                subject = self.ask('So your mean is open, high or low?', False)
            elif intent in (u'mood_affirm', u'mood_great'):
                subject = 'current'
            self.do_stock(stock, subject)

        elif subject.lower().endswith('price'):
            self.do_stock(stock, subject[:-5].strip())

        elif subject in ('open', 'current', 'high', 'low'):
            stock = self.get_stock(stock)
            if stock is None:
                self.response('Failed to get the %s price with unclear reasons.' % subject)
            else:
                self.response('The %s price of stock %s is $%s per share.' % (subject.encode('utf-8'), stock['Name'], stock[subject]))
        
        elif subject == 'volume':
            stock = self.get_stock(stock)
            if stock is None:
                self.response('Failed to get the %s price with unclear reasons.' % subject)
            else:
                self.response('The volume of stock %s is %d.' % stock['volume'])
    
        else:
            self.response('There are too many informations that I know, please ask me a specific stock')

    def do_news(self, news=None, i=0, key=None):
        if not news:
            news = self.get_news(key)
            print news
        self.response(news[i].Title)

        intent = self.ask('Do you interest it?')['intent']
        if intent in (u'mood_deny', u'mood_unhappy'):
            self.do_news(news, i+1)
        if intent in (u'mood_affirm', u'mood_great'):
            self.response('Link of this news is %s' % news[i].Link)

    def get_news(self, subject):
        text = get(NEWS_ADDR % subject).text
        soup = BeautifulSoup(text, 'html.parser')
        infos = soup.findAll(attrs={'class': 'r-info r-info2'})
        return [NEWS_FORMAT(subject, info.a.string.encode('utf-8'), info.a['href']) for info in infos if info.a.string is not None]
        
    def get_stock(self, stock):
        stock_ID, market = self.get_stock_info(stock)
        data = get(STOCK_ADDR % (market, stock_ID)).text.encode('cp936').split('"')[1].split(',')
        try:
            if market in ('sh', 'sz'):
                data = {'Name': data[0],
                        'open': data[1],
                        'high': data[4],
                        'low': data[5],
                        'current': data[3],
                        'volume': data[8]}
            elif market == 'gb_':
                data = {'Name': data[0],
                        'open': data[5],
                        'high': data[6],
                        'low': data[7],
                        'current': data[1],
                        'volume': data[10]}
            elif market == 'hk':
                data = {'Name': data[1],
                        'open': data[2],
                        'high': data[4],
                        'low': data[5],
                        'current': data[6],
                        'volume': data[12]}
            elif market == 'int_':
                return data[1]
            return data
        except:
            return None

    def get_stock_info(self, stock):
        with sql.connect('STOCK_NUM.db') as conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM stocks WHERE Name="%s"' % stock.lower())
            data = cur.fetchone()
        if data is not None:
            return data[0][1:].lower(), data[2]
        self.response("Sorry, I didn't get the information from my database.")
        return '', ''
