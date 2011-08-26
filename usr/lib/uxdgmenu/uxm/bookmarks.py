import os, urllib
from . import base

class BookmarksMenu(base.Menu):

    def parse_config(self):
        super(BookmarksMenu, self).parse_config()
        self.file_manager = self.config.get("Menu", "filemanager")
        if self.show_icons:
            self.bookmark_icon = self.config.get("Icons", "bookmarks")

    def parse_bookmarks(self):
        #icon = self.icon_finder.find_by_name(self.bookmark_icon) if self.show_icons else ''
        bookmarks = [ ('~', 'Home') ]
        append = bookmarks.append
        with open(os.path.expanduser('~/.gtk-bookmarks')) as f:
            for line in f:
                path, label = line.strip().partition(' ')[::2]
                if not label:
                    label = os.path.basename(os.path.normpath(path))
                append((path, label))
        output = []
        append = output.append
        fm = self.file_manager
        for path, label in bookmarks:
            label = urllib.unquote(label)
            cmd = '%s "%s"' % (fm, path)
            path = path.replace('file://', '')
            icon = self.icon_finder.find_by_file_path(path) if self.show_icons else ''
            item = self.formatter.format_application(label, cmd, icon)
            append(item)
        return self.formatter.format_menu("bookmarks", "".join(output))
