import sys

TYPE_INVALID = 0
TYPE_DIRECTORY = 1
TYPE_ENTRY = 2
TYPE_SEPARATOR = 3
TYPE_HEADER = 4
TYPE_ALIAS = 5

NONE = 0
INCLUDE_EXCLUDED = 1
SHOW_EMPTY = 2
INCLUDE_NODISPLAY = 3
SHOW_ALL_SEPARATORS = 4

SORT_NAME = 0
SORT_DISPLAY_NAME = 1


def get_default_adapter():
    try:
        from uxm.adapters import gmenu_adapter
        return gmenu_adapter.GmenuAdapter()
    except ImportError:
        from uxm.adapters import xdg_adapter
        return xdg_adapter.XdgAdapter()

def get_adapter(name):
    if not name in['gmenu', 'xdg']:
        raise ValueError
    else:
        adapter_name = "uxdgmenu.adapters.%s_adapter" % name
        adapter_class = "%sAdapter" % (name[0].upper() + name[1:])
        __import__(adapter_name)
        module = sys.modules[adapter_name]
        adapter = getattr(module, adapter_class)
        return adapter()

def get_by_precedence(names):
    for name in names:
        try:
            return get_adapter(name)
        except:
            continue


class Adapter(object):
    def __init__(self, adaptee):
        self.adaptee = adaptee

class TreeAdapter(object):
    def get_type(self):
        return TYPE_DIRECTORY
    def parse(self, menu_file, flags=NONE):
        raise NotImplementedError

class DirectoryAdapter(Adapter):
    def get_type(self):
        return TYPE_DIRECTORY
    def get_menu_id(self):
        raise NotImplementedError
    def get_name(self):
        raise NotImplementedError
    def get_icon(self):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

class EntryAdapter(Adapter):
    def get_type(self):
        return TYPE_ENTRY;
    def get_desktop_file_path(self):
        raise NotImplementedError
    def get_display_name(self):
        raise NotImplementedError
    def get_icon(self):
        raise NotImplementedError
    def get_exec(self):
        raise NotImplementedError
    def get_launch_in_terminal(self):
        raise NotImplementedError

class SeparatorAdapter(Adapter):
    def get_type(self):
        return TYPE_SEPARATOR;
