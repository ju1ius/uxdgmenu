try:
    import cPickle as pickle
except ImportError:
    import pickle

import uxm.formatter

class PickleFormatter(uxm.formatter.Formatter):

    def format_rootmenu(self, data):
        return self.format_menu(data)

    def format_menu(self, data):
        return pickle.dumps(data, pickle.HIGHEST_PROTOCOL)

    def format_text_item(self, data, level=0):
        pass
    def format_include(self, data, level=0):
        pass
    def format_separator(self, data, level=0):
        pass
    def format_application(self, data, level=0):
        pass
    def format_submenu(self, data, level=0):
        pass
    def format_wm_menu(self, data, level=0):
        pass
