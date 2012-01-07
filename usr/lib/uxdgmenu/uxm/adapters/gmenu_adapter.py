import gmenu

from uxm.adapters import NONE, TYPE_DIRECTORY, TYPE_ENTRY, TYPE_SEPARATOR

class GmenuAdapter(object):
    def get_type(self):
        return TYPE_DIRECTORY;
    def get_root_directory(self, menu_file, flags=NONE):
        tree = gmenu.lookup_tree(menu_file, flags)
        return GmenuDirectoryAdapter(tree.get_root_directory())

class GmenuDirectoryAdapter(object):
    def __init__(self, adaptee):
        self.adaptee = adaptee

    def get_type(self):
        return TYPE_DIRECTORY;

    def get_menu_id(self):
        return self.adaptee.get_menu_id()
    def get_name(self):
        return self.adaptee.get_name()
    def get_icon(self):
        return self.adaptee.get_icon()

    def get_contents(self):
        for entry in self.adaptee.get_contents():
            t = entry.get_type()
            if t == gmenu.TYPE_SEPARATOR:
                yield GmenuSeparatorAdapter()
            elif t == gmenu.TYPE_DIRECTORY:
                yield GmenuDirectoryAdapter(entry)
            elif t == gmenu.TYPE_ENTRY:
                yield GmenuEntryAdapter(entry)

class GmenuEntryAdapter(object):
    
    def __init__(self, adaptee):
        self.adaptee = adaptee

    def get_type(self):
        return TYPE_ENTRY;

    def get_desktop_file_path(self):
        return self.adaptee.get_desktop_file_path()
    def get_display_name(self):
        return self.adaptee.get_display_name()
    def get_icon(self):
        return self.adaptee.get_icon()
    def get_exec(self):
        return self.adaptee.get_exec()
    def get_launch_in_terminal(self):
        return self.adaptee.get_launch_in_terminal()


class GmenuSeparatorAdapter(object):
    def get_type(self):
        return TYPE_SEPARATOR;
