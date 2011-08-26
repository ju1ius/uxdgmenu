import cXdg.Menu
from . import NONE, TYPE_DIRECTORY, TYPE_ENTRY, TYPE_SEPARATOR

class CXdgAdapter(object):
    def get_type(self):
        return TYPE_DIRECTORY;
    def get_root_directory(self, menu_file, flags=NONE):
        return CXdgDirectoryAdapter(cXdg.Menu.parse(menu_file))

class CXdgDirectoryAdapter(object):
    def __init__(self, adaptee):
        self.adaptee = adaptee

    def get_type(self):
        return TYPE_DIRECTORY;

    def get_menu_id(self):
        return self.adaptee.Name
    def get_name(self):
        return self.adaptee.getName()
    def get_icon(self):
        return self.adaptee.getIcon()

    def get_contents(self):
        for entry in self.adaptee.getEntries():
            if isinstance(entry, cXdg.Menu.Separator):
                yield CXdgSeparatorAdapter()
            elif isinstance(entry, cXdg.Menu.Menu):
                yield CXdgDirectoryAdapter(entry)
            elif isinstance(entry, cXdg.Menu.MenuEntry):
                yield CXdgEntryAdapter(entry)

class CXdgEntryAdapter(object):
    
    def __init__(self, adaptee):
        self.adaptee = adaptee
        self.entry = adaptee.DesktopEntry

    def get_type(self):
        return TYPE_ENTRY;

    def get_desktop_file_path(self):
        return self.entry.getFileName()
    def get_display_name(self):
        return self.entry.getName()
    def get_icon(self):
        return self.entry.getIcon()
    def get_exec(self):
        return self.entry.getExec()
    def get_launch_in_terminal(self):
        return self.entry.getTerminal()


class CXdgSeparatorAdapter(object):
    def get_type(self):
        return TYPE_SEPARATOR;

