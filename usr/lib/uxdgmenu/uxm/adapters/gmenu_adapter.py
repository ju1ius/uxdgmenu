import gmenu

from uxm.adapters import TreeAdapter, DirectoryAdapter, EntryAdapter, SeparatorAdapter

class GmenuAdapter(TreeAdapter):

    def parse(self, menu_file, show_hidden=True):
        flags = gmenu.FLAGS_NONE
        if show_hidden:
            flags |= gmenu.FLAGS_INCLUDE_NODISPLAY|gmenu.FLAGS_INCLUDE_EXCLUDED
        tree = gmenu.lookup_tree(menu_file, flags)
        return GmenuDirectoryAdapter(tree.get_root_directory())


class GmenuDirectoryAdapter(DirectoryAdapter):

    def get_name(self):
        return self.adaptee.get_menu_id()

    def get_display_name(self):
       return self.adaptee.get_name()

    def get_filename(self):
        return self.adaptee.get_desktop_file_path()

    def get_icon(self):
        return self.adaptee.get_icon()

    def __iter__(self):
        for entry in self.adaptee.get_contents():
            t = entry.get_type()
            if t == gmenu.TYPE_SEPARATOR:
                yield GmenuSeparatorAdapter(entry)
            elif t == gmenu.TYPE_DIRECTORY:
                yield GmenuDirectoryAdapter(entry)
            elif t == gmenu.TYPE_ENTRY:
                yield GmenuEntryAdapter(entry)


class GmenuEntryAdapter(EntryAdapter):

    def get_filename(self):
        return self.adaptee.get_desktop_file_path()

    def get_display_name(self):
        return self.adaptee.get_display_name()

    def get_icon(self):
        return self.adaptee.get_icon()

    def get_exec(self):
        return self.adaptee.get_exec()

    def is_terminal(self):
        return self.adaptee.get_launch_in_terminal()

    def is_visible(self):
        return not self.adaptee.get_is_excluded()


class GmenuSeparatorAdapter(SeparatorAdapter):
    pass
