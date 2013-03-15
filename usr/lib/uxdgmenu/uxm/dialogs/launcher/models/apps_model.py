import os
import re
import shlex
import cPickle as pickle
import operator
import multiprocessing
import threading

import gobject
import glib
import gtk

import uxm.cache
import uxm.bench as bench
import uxm.config as config
import uxm.utils.mime
import uxm.utils.fs
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
        self.data = {}
        self.stemmer = SimpleStemmer(self.terminal)

    def configure(self):
        self.terminal = self.prefs.get('General', 'terminal')
        self.dir_icon = self.icon_finder.find_by_mime_type(
            uxm.utils.mime.INODE_DIR, False
        )
        self.dir_link_icon = self.icon_finder.find_by_mime_type(
            uxm.utils.mime.INODE_DIR, True
        )
        self.exe_icon = self.icon_finder.find_by_mime_type(
            'application/x-executable', False
        )
        self.exe_link_icon = self.icon_finder.find_by_mime_type(
            'application/x-executable', True
        )

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
        apps_cmds = set()
        for item in self.iter_menu(apps):
            item['type'] = model.TYPE_APP
            item['mimetype'] = uxm.utils.mime.APP_EXE
            self.append_item(item, count, True)
            apps_cmds.add(item['command'])
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
        # Fetching mimetype for all files in PATH can take quite a long time,
        # especially if the disk cache is empty, eg on a fresh start.
        # So we just get basic info and fetch the real mimetype later
        path_cmds = []
        for app_path in self.iter_path():
            name = os.path.basename(app_path)
            # don't index executables found in desktop apps
            if name in apps_cmds or app_path in apps_cmds:
                continue
            if name.startswith('less'):
                print name, app_path
            self.index.add(name, {'id': count})
            is_link = os.path.islink(app_path)
            if os.path.isdir(app_path):
                icon = self.dir_link_icon if is_link else self.dir_icon
                type = model.TYPE_DIR
                mt = uxm.utils.mime.INODE_DIR
            if os.path.isfile(app_path):
                type = model.TYPE_CMD
                icon = self.exe_link_icon if is_link else self.exe_icon
                mt = uxm.utils.mime.APP_EXE
                path_cmds.append((app_path, name, is_link, count))
            else:
                continue
            self.data[count] = {
                'id': count,
                'type': type,
                'label': name,
                'command': name,
                'icon': icon,
                'mimetype': mt
            }
            count += 1
        # now reload mimetypes asynchronously
        self.reload_path_info_async(path_cmds)
        bench.endstep('Load apps')

    def append_item(self, item, id, stem_command=False):
        doc = {'id': id}
        item['id'] = id
        for word in self.stemmer.stem_phrase(item['label']):
            self.index.add(word, doc)
        if stem_command:
            for word in self.stemmer.stem_command(item['command']):
                self.index.add(word, doc)
        self.data[id] = item

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
        cmds = set()
        for d in reversed(os.environ['PATH'].split(':')):
            for f in os.listdir(d):
                if f in cmds:
                    continue
                fp = os.path.join(d, f)
                if os.path.isfile(fp):
                    cmds.add(f)
                    yield fp

    def find_app_in_path(self, path):
        icon = self.icon_finder.find_by_file_path(path)
        return path, icon

    def parse_query(self, terms):
        for word in self.stemmer.stem_phrase(terms, 0):
            yield word

    def reload_path_info_async(self, apps):
        """Reloads mime type information for apps in PATH asynchronously"""
        manager = multiprocessing.Manager()
        queue = manager.Queue()
        pool = multiprocessing.Pool(processes=2)
        num_apps = len(apps)
        self.listener = QueueListener(queue, num_apps)
        self.listener.connect('updated', self.on_path_info_updated)
        # Starting Listener
        thread = threading.Thread(target=self.listener.run, args=())
        thread.start()
        for app in apps:
            pool.apply_async(_get_content_type, (app, queue))
        pool.close()

    def kill_threads(self):
        """This MUST be called on program exit or the background thread(s)
        will block until finished
        """
        self.listener.stop()

    def on_path_info_updated(self, listener, data):
        mimetype, path, name, is_link, id = data
        icon = self.icon_finder.find_by_mime_type(mimetype, is_link)
        self.data[id]['icon'] = icon
        self.data[id]['mimetype'] = mimetype


def _get_content_type(appinfo, queue):
    """The actual mimetype worker"""
    path, name, is_link, id = appinfo
    mimetype = uxm.utils.mime.guess(path)
    result = (mimetype, path, name, is_link, id)
    queue.put(result)


class SimpleStemmer(object):
    """Minimal stemmer for the indexer
    Just splits words on unicode whitespace characters,
    plus hyphens and underscores
    """
    MIN_WORD_LEN = 1
    WORD_RX = re.compile(r'[-_\W]*', re.L | re.U)

    def __init__(self, terminal):
        self.terminal = terminal

    def stem_phrase(self, phrase, min_len=None):
        min_len = self.MIN_WORD_LEN if min_len is None else min_len
        words = self.WORD_RX.split(phrase)
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
            for word in self.WORD_RX.split(exe):
                if len(word) > self.MIN_WORD_LEN:
                    yield word


class QueueListener(gobject.GObject):
    __gsignals__ = {
        'updated': (
            gobject.SIGNAL_RUN_LAST,
            gobject.TYPE_NONE,
            (gobject.TYPE_PYOBJECT,)
        ),
        'error': (
            gobject.SIGNAL_RUN_LAST,
            gobject.TYPE_NONE,
            (gobject.TYPE_STRING,)
        ),
        'finished': (
            gobject.SIGNAL_RUN_LAST,
            gobject.TYPE_NONE,
            ()
        )
    }

    def __init__(self, queue, max_results):
        gobject.GObject.__init__(self)
        self.queue = queue
        self.max_results = max_results
        self.num_results = 0
        self.stopevent = threading.Event()

    def emit(self, *args):
        """Ensures signals are emitted in the main thread"""
        glib.idle_add(gobject.GObject.emit, self, *args)

    def run(self):
        if self.queue is None:
            raise RuntimeError('Listener must be associated with a Queue')
        bench.step('Load path')
        while not self.stopevent.isSet():
            # Listen for results on the queue and process them accordingly
            data = self.queue.get()
            # Check if finished
            self.num_results += 1
            if self.num_results == self.max_results:
                bench.endstep('Load path')
                self.emit("finished")
                self.stop()
            elif data[0] == "error":
                self.emit('error', data[1])
                self.stop()
            else:
                self.emit('updated', data)

    def stop(self):
        self.stopevent.set()
