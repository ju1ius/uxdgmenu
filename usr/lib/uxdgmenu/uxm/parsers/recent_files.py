import os, sys, re, urllib

import uxm.parser as parser
import uxm.config as config

try:
    from xml.etree import cElementTree as ElementTree
except:
    from xml.etree import ElementTree

_ = config.translate

MIME_TYPE_NS = 'http://www.freedesktop.org/standards/shared-mime-info'
BOOKMARK_NS  = 'http://www.freedesktop.org/standards/desktop-bookmarks' 
MIME_EXPR    = 'info/metadata/{%s}mime-type' % MIME_TYPE_NS
BOOKMARK_EXPR = 'info/metadata/{%(ns)s}applications/{%(ns)s}application' % {
    "ns": BOOKMARK_NS
}

class Parser(parser.BaseParser):

    def __init__(self):
        super(Parser, self).__init__()
        self.exe_regex = re.compile(r"'(.*) %[a-zA-Z]'")
        self.max_items = self.config.getint("Recent Files", "max_items")
        if self.show_icons:
            self.clear_icon = self.icon_finder.find_by_name('gtk-clear')
        else:
            self.clear_icon = ''

    def parse_bookmarks(self):
        if not os.path.exists(config.RECENT_FILES_FILE):
            self.create_default()
        tree = ElementTree.parse(config.RECENT_FILES_FILE)
        last_index = - (self.max_items -1)
        bookmarks = tree.findall('./bookmark')[last_index:-1]
        bookmarks.reverse()
        items = map(self.parse_item, bookmarks)
        items.extend([
            { "type": "separator" },
            {
                "type": "application",
                "label": _('Clear List'),
                "command": "uxm-daemon clear-recent-files",
                "icon": self.clear_icon
            }
        ])
        return {
            "type": "menu",
            "label": "Recent Files",
            "id": "uxdgmenu-recent-files",
            "icon": "",
            "items": items
        }

    def parse_item(self, el):
        href = el.get('href')
        label = urllib.unquote( href.rsplit('/',1)[1] )
        cmd = el.find(BOOKMARK_EXPR).get('exec')
        cmd = self.exe_regex.sub(r'\1', cmd)
        cmd = '%s "%s"' % (cmd, href)
        mime_type = el.find(MIME_EXPR).get('type')
        icon = self.icon_finder.find_by_mime_type(mime_type) if self.show_icons else ''
        return {
            "type": "application",
            "label": label.encode('utf-8'),
            "icon": icon.encode('utf-8'),
            "command": cmd.encode('utf-8')
        }

    def create_default(self):
        with open(config.RECENT_FILES_FILE, 'w') as f:
            f.write("""<?xml version="1.0" encoding="UTF-8"?>
<xbel version="1.0"
      xmlns:bookmark="http://www.freedesktop.org/standards/desktop-bookmarks"
      xmlns:mime="http://www.freedesktop.org/standards/shared-mime-info"
>
</xbel>""")
