import os
import re
import shlex
import cPickle as pickle
import operator
import multiprocessing
import gtk

import uxm.bench as bench
import uxm.config as config
import uxm.utils
from . import model
from . import utils
from .index import Index

APPS_MENU = '%s.pckl' % config.APPS_CACHE
BOOK_MENU = '%s.pckl' % config.BOOKMARKS_CACHE
RECENT_MENU = '%s.pckl' % config.RECENT_FILES_CACHE


class AppsModel(model.Model):

    def __init__(self):
        super(AppsModel, self).__init__()
        self.index = Index()
        self.data = []
        self.stemmer = SimpleStemmer(self.terminal)

    def configure(self):
        self.terminal = self.prefs.get('General', 'terminal')

    def find(self, query):
        terms = self.parse_query(query)
        ids = self.index.find(terms)
        items = (self.data[id] for id in ids)
        self.model.clear()
        for item in sorted(items, key=operator.itemgetter('type')):
            icon = item['icon']
            pixbuf = utils.load_icon(icon)
            self.model.append((
                item['id'], item['type'],
                item['label'], pixbuf,
                item['mimetype']
            ))
        return ids

    def get_action_menu(self, id):
        item = self.data[id]
        actions = item['items']
        menu = gtk.Menu()
        for action in actions:
            if 'application' == action['type']:
                if action['icon']:
                    img = gtk.Image()
                    img.set_from_file(action['icon'])
                    menuitem = gtk.ImageMenuItem(gtk.STOCK_EXECUTE)
                    menuitem.set_image(img)
                    menuitem.set_label(action['label'])
                else:
                    menuitem = gtk.MenuItem(action['label'])
                menuitem.command = action['command']
            elif 'separator' == action['type']:
                menuitem = gtk.SeparatorMenuItem()
            elif 'text' == action['type']:
                menuitem = gtk.MenuItem(action['label'])
            menu.append(menuitem)
        return menu

    def get_default_action(self, id):
        """Returns the default action for an item
        (the first command found in it's actions list)
        """
        item = self.data[id]
        actions = item['items']
        for action in actions:
            if 'application' == action['type']:
                return action['command']

    def load(self):
        bench.step('Load apps')
        count = len(self.data)
        apps = self.load_pickle(APPS_MENU)
        for item in self.iter_menu(apps):
            item['type'] = model.TYPE_APP
            item['mimetype'] = uxm.utils.mime.APP_EXE
            self.append_item(item, count, True)
            count += 1
        bookmarks = self.load_pickle(BOOK_MENU)
        for item in self.iter_bookmarks(bookmarks):
            item['type'] = model.TYPE_DIR
            item['mimetype'] = uxm.utils.mime.INODE_DIR
            self.append_item(item, count, False)
            count += 1
        recent_files = self.load_pickle(RECENT_MENU)
        for item in self.iter_recent_files(recent_files):
            item['type'] = model.TYPE_FILE
            item['url'] = item['id']
            self.append_item(item, count, False)
            count += 1
        # Fetching infos for all files in PATH can take quite a long time,
        # so we try to parallelize that
        pool = multiprocessing.Pool()
        app_infos = pool.map(_get_content_type, [p for p in self.iter_path()], 16)
        for path, mt in app_infos:
            name = os.path.basename(path)
            self.index.add(name, {'id': count})
            icon = self.icon_finder.find_by_mime_type(
                mt,
                os.path.islink(path),
                uxm.utils.mime.APP_EXE
            )
            self.data.append({
                'id': count,
                'type': model.TYPE_CMD,
                'label': name,
                'command': name,
                'icon': icon,
                'mimetype': mt
            })
            count += 1
        bench.endstep('Load apps')

    def append_item(self, item, id, stem_command=False):
        doc = {'id': id}
        item['id'] = id
        for word in self.stemmer.stem_phrase(item['label']):
            self.index.add(word, doc)
        if stem_command:
            for word in self.stemmer.stem_command(item['command']):
                self.index.add(word, doc)
        self.data.append(item)

    def load_pickle(self, filepath):
        f = os.path.expanduser(filepath)
        with open(f, 'r') as fp:
            return pickle.load(fp)

    def iter_menu(self, item):
        if 'application' == item['type']:
            yield item
        elif 'menu' == item['type']:
            for child_item in item['items']:
                for child in self.iter_menu(child_item):
                    yield child

    def iter_recent_files(self, root):
        for child in root['items']:
            if child['type'] == 'menu':
                yield child

    def iter_bookmarks(self, root):
        for child in root['items']:
            if child['type'] == 'application':
                yield child

    def iter_path(self):
        for d in os.environ['PATH'].split(':'):
            for f in os.listdir(d):
                fp = os.path.join(d, f)
                if os.path.isfile(fp):
                    yield fp

    def find_app_in_path(self, path):
        icon = self.icon_finder.find_by_file_path(path)
        return path, icon

    def parse_query(self, terms):
        for word in self.stemmer.stem_phrase(terms, 0):
            yield word


def _get_content_type(path):
    t = uxm.utils.mime.guess(path)
    return path, t


WORD_RX = re.compile(r'[-_\W]*', re.L | re.U)


class SimpleStemmer(object):

    MIN_WORD_LEN = 1

    def __init__(self, terminal):
        self.terminal = terminal

    def stem_phrase(self, phrase, min_len=None):
        min_len = self.MIN_WORD_LEN if min_len is None else min_len
        words = WORD_RX.split(phrase)
        for word in words:
            if len(word) > min_len:
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
            exe = arg[pos + 1:]
            for word in WORD_RX.split(exe):
                if len(word) > self.MIN_WORD_LEN:
                    yield word
