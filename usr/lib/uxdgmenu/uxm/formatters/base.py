from collections import deque
from pprint import pprint as pp

class Formatter(object):

    indent_str = "  "

    def indent(self, level=0):
        return self.indent_str * level

    def get_name(self):
        return self.__module__.split('.')[-1]
    
    def format_rootmenu(self, content):
        self._implement_error("format_rootmenu")

    def format_menu(self, id, content):
        self._implement_error("format_menu")

    def format_text_item(self, txt, level=0):
        self._implement_error("format_text_item")

    def format_separator(self, level=0):
        self._implement_error("format_separator")

    def format_application(self, name, cmd, icon, level=0):
        self._implement_error("format_application")

    def format_submenu(self, id, name, icon, submenu, level=0):
        self._implement_error("format_submenu")

    def _implement_error(self, method):
        cls = str(self.__class__.__bases__[-1])
        raise NotImplementedError(
            "Subclasses of %s must implement a %s method" % (
                cls, method
            )
        )

class TreeFormatter(Formatter):

    def get_children(self, data, level=0):
        for item in data['items']:
            if item['type'] == 'application':
                yield self.format_application(item, level+1)
            elif item['type'] == 'separator':
                yield self.format_separator(level+1)
            elif item['type'] == 'menu':
                yield self.format_submenu(item, level+1)
            elif item['type'] == 'text':
                yield self.format_text_item(item, level+1)

class FlatFormatter(Formatter):

    submenus_first = False

    def format_submenu_entry(self, data, level=0):
        self._implement_error("format_submenu_entry")

    def get_children(self, data, submenus_first=True):
        output = []
        entries = []
        submenus = []
        items = data['items']
        add_submenus = submenus.extend
        add_entry = entries.append
        for item in items:
            if item['type'] == 'menu':
                add_submenus(self.get_children(item))
        for item in items:
            if item['type'] == 'menu':
                add_entry(self.format_submenu_entry(item))
            elif item['type'] == 'application':
                add_entry(self.format_application(item))
            elif item['type'] == 'separator':
                add_entry(self.format_separator(item))
        if submenus_first: output.extend(submenus)
        output.append(self.format_submenu(data, entries))
        if not submenus_first: output.extend(submenus)
        return output
