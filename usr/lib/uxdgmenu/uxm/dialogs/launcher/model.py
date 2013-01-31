import os, re, shlex
import cPickle as pickle

import gtk

from .index import Index
from .constants import *
import uxm.config as config

APPS_MENU =   '%s.pckl' % config.APPS_CACHE


class Model(object):

    def __init__(self):
        self.prefs = config.preferences()
        self.terminal = self.prefs.get('General', 'terminal')
        
        self.index = Index()
        self.store = gtk.ListStore(*COLUMNS)
        self.data = []
        self.stemmer = SimpleStemmer(self.terminal)

    def find(self, query):
        terms = self.parse_query(query)
        ids = self.index.find(terms)
        self.store.clear()
        for id in ids:
            item = self.data[id]
            icon = item['icon']
            pixbuf = load_icon(icon)
            self.store.append((
                id, TYPE_APP,
                item['label'], pixbuf
            ))
        return ids

    def load_apps(self):
        data = self.load_data(APPS_MENU)
        counter = len(self.data)
        for app in self.iter_menu(data):
            doc = {'id': counter}
            app['type'] = TYPE_APP
            for word in self.stemmer.stem_phrase(app['label']):
                self.index.add(word, doc)
            for word in self.stemmer.stem_command(app['command']):
                self.index.add(word, doc)
            self.data.append(app)
            counter += 1

    def load_data(self, filepath):
        f = os.path.expanduser(filepath)
        with open (f, 'r') as fp:
            return pickle.load(fp)

    def iter_menu(self, item):
        #print item['type'], item['label']
        if 'application' == item['type']:
            yield item
        elif 'menu' == item['type']:
            for child_item in item['items']:
                for child in self.iter_menu(child_item):
                    yield child

    def parse_query(self, terms):
        for word in self.stemmer.stem_phrase(terms):
            yield word


WORD_RX = re.compile(r'[-_\W]*', re.L|re.U)

class SimpleStemmer(object):

    MIN_WORD_LEN = 1

    def __init__(self, terminal):
        self.terminal = terminal

    def stem_phrase(self, phrase):
        words = WORD_RX.split(phrase)
        for word in words:
            if len(word) > self.MIN_WORD_LEN:
                yield word.lower()

    def stem_command(self, cmd):
        cmd = cmd.replace(self.terminal, '')
        cmd = shlex.split(cmd)
        for arg in cmd:
            if '-' == arg[0]:
                continue
            pos = arg.rfind('/')
            if -1 == pos:
                exe = arg
            exe = arg[pos+1:]
            for word in WORD_RX.split(exe):
                if len(word) > self.MIN_WORD_LEN:
                    yield word

