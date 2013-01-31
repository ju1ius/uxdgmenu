import os, subprocess
import cPickle as pickle
import gtk

import uxm.config as config

APPS_MENU =   '%s.pckl' % config.APPS_CACHE

(
    COLUMN_TYPE,
    COLUMN_SEARCH,
    COLUMN_NAME,
    COLUMN_PATH,
    COLUMN_ICON
) = range(5)

(
    MODE_APPS, MODE_BOOK, MODE_RECENT, MODE_PLACES, MODE_DEVICES
) = range(5)

class Launcher(object):

    def __init__(self):
        self.current_mode = MODE_APPS
        self.current_search = ""

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_size_request(500, 300)

        self.model = gtk.ListStore(str, str, str, str, str)
        #self.model_filter = self.model.filter_new()
        #self.model_filter.set_visible_func(self.search_callback)

        self.entry = gtk.Entry()
        self.completion = gtk.EntryCompletion()
        self.completion.set_model(self.model)
        self.completion.set_inline_completion(True)
        self.completion.set_inline_selection(True)
        self.completion.set_text_column(COLUMN_SEARCH)
        self.completion.set_match_func(self.search_callback)
        self.entry.set_completion(self.completion)

        self.window.add(self.entry)
        self.window.connect('delete-event', gtk.main_quit)
        self.window.connect('key-press-event', self.on_key_press)
        self.window.show_all()

    def on_key_press(self, widget, event, data=None):
        key = event.keyval
        if gtk.keysyms.Escape == key:
            gtk.main_quit()
        elif gtk.keysyms.Tab == key:
            self.completion.insert_prefix()

    def search_callback(self, completion, key_string, it, data=None):
        pattern = key_string.lower()
        subject = completion.get_model().get_value(it, COLUMN_SEARCH)
        return subject.find(pattern) != -1

    def load_apps(self):
        data = self.load_data(APPS_MENU)
        for app in self.iter_menu(data):
            search_subject = app['label'].lower() + app['command'].split(' ')[0]
            self.model.append((
                'app', search_subject,
                app['label'], app['command'], app['icon']
            ))

    def load_data(self, filepath):
        f = os.path.expanduser(filepath)
        with open (f, 'r') as fp:
            return pickle.load(fp)

    def iter_menu(self, item, output=[]):
        if 'application' == item['type']:
            yield item
        elif 'menu' == item['type']:
            for child_item in item['items']:
                for child in self.iter_menu(child_item):
                    yield child
