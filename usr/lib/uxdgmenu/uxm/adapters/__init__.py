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
        import gmenu
        from . import gmenu_adapter
        return gmenu_adapter.GmenuAdapter()
    except ImportError:
        from . import xdg_adapter
        return xdg_adapter.XdgAdapter()

def get_adapter(name):
    if not name in['gmenu', 'xdg', 'cXdg']:
        raise ValueError
    else:
        adapter_name = "uxdgmenu.adapters.%s_adapter" % name
        adapter_class = "%sAdapter" % (name[0].upper() + name[1:])
        __import__(adapter_name)
        module = sys.modules[adapter_name]
        adapter = getattr(module, adapter_class)
        return adapter()
