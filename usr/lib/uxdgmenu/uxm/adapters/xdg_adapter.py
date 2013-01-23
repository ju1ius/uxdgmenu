import xdg.Menu

from uxm.adapters import NONE, TreeAdapter, DirectoryAdapter, EntryAdapter, SeparatorAdapter

class XdgAdapter(TreeAdapter):
    def parse(self, menu_file, flags=NONE):
        return XdgDirectoryAdapter(xdg.Menu.parse(menu_file))

class XdgDirectoryAdapter(DirectoryAdapter):
    def __init__(self, adaptee):
        self.adaptee = adaptee

    def get_name(self):
        return self.adaptee.Name
    def get_display_name(self):
        return self.adaptee.getName()
    def get_icon(self):
        return self.adaptee.getIcon()
    def get_filename(self):
        return self.adaptee.Directory and \
            self.adaptee.Directory.DesktopEntry.filename \
            or None

    def __iter__(self):
        for entry in self.adaptee.getEntries():
            if isinstance(entry, xdg.Menu.Separator):
                yield XdgSeparatorAdapter(entry)
            elif isinstance(entry, xdg.Menu.Menu):
                yield XdgDirectoryAdapter(entry)
            elif isinstance(entry, xdg.Menu.MenuEntry):
                yield XdgEntryAdapter(entry)

class XdgEntryAdapter(EntryAdapter):
    
    def __init__(self, adaptee):
        self.adaptee = adaptee
        self.entry = adaptee.DesktopEntry

    def get_filename(self):
        return self.entry.getFileName()
    def get_display_name(self):
        return self.entry.getName()
    def get_icon(self):
        return self.entry.getIcon()
    def get_exec(self):
        return self.entry.getExec()
    def is_terminal(self):
        return self.entry.getTerminal()
    def is_visible(self):
        return self.adaptee.Show is True


class XdgSeparatorAdapter(SeparatorAdapter):
    pass
