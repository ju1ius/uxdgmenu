import json

import uxm.formatter

class Formatter(uxm.formatter.TreeFormatter):

    def format_rootmenu(self, data):
        return json.dumps(data)

    def format_menu(self, data):
        return json.dumps(data)

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
