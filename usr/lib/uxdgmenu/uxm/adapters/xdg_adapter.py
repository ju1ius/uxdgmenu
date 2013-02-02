import xdg.Menu

from uxm.adapters import NONE, TreeAdapter, DirectoryAdapter, EntryAdapter, SeparatorAdapter

def factory(entry):
    if isinstance(entry, xdg.Menu.Separator):
        return XdgSeparatorAdapter(entry)
    elif isinstance(entry, xdg.Menu.Menu):
        return XdgDirectoryAdapter(entry)
    elif isinstance(entry, xdg.Menu.MenuEntry):
        return XdgEntryAdapter(entry)

class XdgAdapter(TreeAdapter):
    def parse(self, menu_file, show_hidden=True):
        return XdgDirectoryAdapter(xdg.Menu.parse(menu_file), show_hidden)

class XdgDirectoryAdapter(DirectoryAdapter):
    def __init__(self, adaptee, show_hidden=True):
        self.adaptee = adaptee
        self.show_hidden = show_hidden

    def get_name(self):
        return self.adaptee.Name
    def get_display_name(self):
        return self.adaptee.getName()
    def get_icon(self):
        return self.adaptee.getIcon()
    def get_filename(self):
        d = self.adaptee.Directory
        return d and d.DesktopEntry.filename or None
    def get_comment(self):
        self.adaptee.getComment()

    def __iter__(self):
        for entry in self.adaptee.getEntries(self.show_hidden):
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
    def get_comment(self):
        return self.entry.getComment()


class XdgSeparatorAdapter(SeparatorAdapter):
    pass
