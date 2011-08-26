import os, sys, re, urllib
from . import base
try:
    from xml.etree import cElementTree as ElementTree
except:
    from xml.etree import ElementTree

import gettext
__t = gettext.translation("fluxdgmenu", "/usr/share/locale")
_ = __t.ugettext

class RecentlyUsedMenu(base.Menu):

    def __init__(self, formatter):
        super(RecentlyUsedMenu, self).__init__(formatter)
        self.exe_regex = re.compile(r"'(.*) %[a-zA-Z]'")
        self.mime_type_ns = 'http://www.freedesktop.org/standards/shared-mime-info'
        self.bookmark_ns = 'http://www.freedesktop.org/standards/desktop-bookmarks' 

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
            self.format_separator(0),
            self.format_application(
                _('Clear List'), 'fxm-daemon clear-recently-used',
                self.icon_finder.find_by_name('gtk-clear') if self.show_icons else '', 
                0
            )
        ])
        return self.format_menu("recently-used", "".join(output) )

    def parse_item(self, el):
        href = el.get('href')
        label = urllib.unquote( href.rsplit('/',1)[1] )
        cmd = self.element_get_exec(el)
        cmd = self.exe_regex.sub(r'\1', cmd)
        cmd = '%s "%s"' % (cmd, href)
        mime_type = self.elemnt_get_mime_type(el)
        icon = self.icon_finder.find_by_mime_type(mime_type) if self.show_icons else ''
        return self.format_application(label, cmd, icon)

    def element_get_exec(element):
        return element.find(
            'info/metadata/{%(ns)s}applications/{%s}application' % self.bookmark_ns
        ).get('exec')

    def elemnt_get_mime_type(element):
        return elemnt.find(
            'info/metadata/{%s}mime-type' % self.mime_type_ns
        ).get('type')
