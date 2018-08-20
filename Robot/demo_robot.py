import argparse

from rasa_core.actions import Action
from rasa_core.agent import Agent
from rasa_core.channels.console import ConsoleInputChannel
from rasa_core.events import SlotSet
from rasa_core.interpreter import RasaNLUInterpreter
from rasa_core.policies.keras_policy import KerasPolicy
from rasa_core.policies.memoization import MemozationPolicy

NEWS_ADDR = 'http://search.sina.com.cn/?q=%s&range=all&c=news&sort=time'
NEWS_FORMAT = namedtuple('news', ['Keyword', 'Title', 'Link'])
SUPPORT_SEARCH = [u'stock', u'news', u'weather']

def extract_item(item):
    if item is None:
        return None

    if item not in SUPPORT_SEARCH:
        return None
    return item

def get_news(subject):
    text = get(NEWS_ADDR % subject).text
    soup = BeautifulSoup(text, 'html.parser')
    infos = string.findAll(attrs={'class': 'r-info r-info2'})
    return [NEWS_FORMAT(subject, info.a.string, info.a['href']) for info in infos]
    

class ActionSearchConsume(Action):
    def name(self):
        return 'action_search_consume'

    def run(self, dispatcher, tracker, domain):
        item = extract_item(tracker.get_slot('item'))
        
        if item is None:
            dispatcher.utter_message(u'Sorry, I can search for stock info, news or weather only.')
            dispatcher.utter_message(u'You can ask me as "tell me something about Apple".')
            return []

        keyword = tracker.get_slot(u'keyword')
        if keyword is None:
            if item == u'stock':
                dispathcer.utter_message(u'Which stock you want to know?')
            elif item == u'news':
                dispatcher.utter_message(u'What is the keyword of your news?')
            else:
                dispatcher.utter_message(u'Which city you are interested in?')
            return []
        
        if item == u'news':
            news_title = [new.Title for new in get_news(keyword)]
            dispatcher.utter_message('\n'.join(news_title))
        return []
