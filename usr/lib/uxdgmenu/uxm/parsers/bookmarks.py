import os
import urllib

import uxm.parser as parser


class Parser(parser.BaseParser):

    def __init__(self):
        super(Parser, self).__init__()
        self.file_manager = self.preferences.get("General", "filemanager")
        if self.show_icons:
            icon = self.preferences.get("Icons", "bookmark")
            self.bookmark_icon = self.icon_finder.find_by_name(icon)
        else:
            self.bookmark_icon = ''

    def parse_bookmarks(self):
        bookmarks = [(os.path.expanduser('~'), 'Home')]
        append = bookmarks.append
        with open(os.path.expanduser('~/.gtk-bookmarks')) as f:
            for line in f:
                path, label = line.strip().partition(' ')[::2]
                path = urllib.unquote(path)
                if not label:
                    label = os.path.basename(os.path.normpath(path))
                append((path.encode('utf-8'), label))
        menu = {
            "type": "menu",
            "id": "uxdgmenu-bookmarks",
            "icon": self.bookmark_icon.encode('utf-8'),
            "items": []
        }
        append = menu['items'].append
        fm = self.file_manager
        for path, label in bookmarks:
            label = urllib.unquote(label)
            cmd = '%s "%s"' % (fm, path)
            path = urllib.unquote(path.replace('file://', ''))
            icon = self.icon_finder.find_by_file_path(path) if self.show_icons else ''
            item = {
                "type": "application",
                "label": label.encode('utf-8'),
                "command": cmd.encode('utf-8'),
                "icon": icon.encode('utf-8')
            }
            append(item)
        return menu
