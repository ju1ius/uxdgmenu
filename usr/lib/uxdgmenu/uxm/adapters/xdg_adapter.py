import xdg.Menu

from uxm.adapters import NONE, TYPE_DIRECTORY, TYPE_ENTRY, TYPE_SEPARATOR

class XdgAdapter(object):
    def get_type(self):
        return TYPE_DIRECTORY;
    def get_root_directory(self, menu_file, flags=NONE):
        return XdgDirectoryAdapter(xdg.Menu.parse(menu_file))

class XdgDirectoryAdapter(object):
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
            if isinstance(entry, xdg.Menu.Separator):
                yield XdgSeparatorAdapter()
            elif isinstance(entry, xdg.Menu.Menu):
                yield XdgDirectoryAdapter(entry)
            elif isinstance(entry, xdg.Menu.MenuEntry):
                yield XdgEntryAdapter(entry)

class XdgEntryAdapter(object):
    
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


class XdgSeparatorAdapter(object):
    def get_type(self):
        return TYPE_SEPARATOR;

