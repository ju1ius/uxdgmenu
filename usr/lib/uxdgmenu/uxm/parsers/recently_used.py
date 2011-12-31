import os, sys, re, urllib
from .. import parser

try:
    from xml.etree import cElementTree as ElementTree
except:
    from xml.etree import ElementTree

import gettext
__t = gettext.translation("fluxdgmenu", "/usr/share/locale")
_ = __t.ugettext

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
        self.max_items = self.config.getint("Recently Used", "max_items")
        if self.show_icons:
            self.clear_icon = self.icon_finder.find_by_name('gtk-clear')
        else:
            self.clear_icon = ''

    def parse_bookmarks(self):
        source = os.path.expanduser("~/.recently-used.xbel")
        tree = ElementTree.parse(source)
        last_index = - (self.max_items -1)
        bookmarks = tree.findall('/bookmark')[last_index:-1]
        bookmarks.reverse()
        items = map(self.parse_item, bookmarks)
        items.extend([
            { "type": "separator" },
            {
                "type": "application",
                "label": _('Clear List'),
                "command": "uxm-daemon clear-recently-used",
                "icon": self.clear_icon
            }
        ])
        return {
            "type": "menu",
            "label": "Recent Files",
            "id": "uxdgmenu-recently-used",
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
