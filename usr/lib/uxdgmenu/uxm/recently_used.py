import os, sys, re, urllib
from . import base
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

class RecentlyUsedMenu(base.Menu):

    def __init__(self, formatter):
        super(RecentlyUsedMenu, self).__init__(formatter)
        self.exe_regex = re.compile(r"'(.*) %[a-zA-Z]'")

    def parse_config(self):
        super(RecentlyUsedMenu, self).parse_config()
        self.max_items = self.config.getint("Recently Used", "max_items")

    def parse_bookmarks(self):
        source = os.path.expanduser("~/.recently-used.xbel")
        tree = ElementTree.parse(source)
        last_index = - (self.max_items -1)
        bookmarks = tree.findall('/bookmark')[last_index:-1]
        bookmarks.reverse()
        output = map(self.parse_item, bookmarks)
        output.extend([
            self.formatter.format_separator(0),
            self.formatter.format_application(
                _('Clear List'), 'uxm-daemon clear-recently-used',
                self.icon_finder.find_by_name('gtk-clear') if self.show_icons else '', 
                0
            )
        ])
        return self.formatter.format_menu("recently-used", "".join(output) )

    def parse_item(self, el):
        href = el.get('href')
        label = urllib.unquote( href.rsplit('/',1)[1] )
        cmd = el.find(BOOKMARK_EXPR).get('exec')
        cmd = self.exe_regex.sub(r'\1', cmd)
        cmd = '%s "%s"' % (cmd, href)
        mime_type = el.find(MIME_EXPR).get('type')
        icon = self.icon_finder.find_by_mime_type(mime_type) if self.show_icons else ''
        return self.formatter.format_application(label, cmd, icon)
