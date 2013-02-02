import os
import re
import urllib

import uxm.parser as parser
import uxm.config as config
from uxm.utils import shell
from uxm.utils import mime

try:
    from lxml import etree
except ImportError:
    try:
        import xml.etree.cElementTree as etree
    except:
        import xml.etree.ElementTree as etree

_ = config.translate

MIME_TYPE_NS = 'http://www.freedesktop.org/standards/shared-mime-info'
BOOKMARK_NS = 'http://www.freedesktop.org/standards/desktop-bookmarks'
MIME_EXPR = 'info/metadata/{%s}mime-type' % MIME_TYPE_NS
BOOKMARK_EXPR = 'info/metadata/{%(ns)s}applications/{%(ns)s}application' % {
    "ns": BOOKMARK_NS
}


class Parser(parser.BaseParser):

    def __init__(self):
        super(Parser, self).__init__()
        #self.exe_regex = re.compile(r"'(.*) %[a-zA-Z]'")
        self.exe_regex = re.compile(r"'.* (%[ufUF])'")
        self.max_items = self.preferences.getint("Recent Files", "max_items")
        if self.show_icons:
            self.clear_icon = self.icon_finder.find_by_name('gtk-clear')
        else:
            self.clear_icon = ''

    def parse_bookmarks(self):
        if not os.path.exists(config.RECENT_FILES_FILE):
            self.create_default()
        tree = etree.parse(config.RECENT_FILES_FILE)
        bookmarks = tree.findall('./bookmark')
        bookmarks.reverse()
        items = []
        count = 1
        for el in bookmarks:
            item = self.parse_item(el)
            if item is None:
                continue
            items.append(item)
            if count == self.max_items:
                break
            count += 1
        items.extend([
            {"type": "separator"},
            {
                "type": "application",
                "label": _('Clear List'),
                "command": "uxm-daemon clear-recent-files",
                "icon": self.clear_icon
            }
        ])
        return {
            "type": "menu",
            "label": "Recently Used",
            "id": "uxm-recent-files",
            "icon": "",
            "items": items
        }

    def parse_item(self, el):
        mime_type = el.find(MIME_EXPR).get('type')
        href = urllib.unquote(el.get('href'))
        protocol, url = href.split('://', 1)
        last_sep = url.rfind('/')
        if last_sep == -1:
            label = url
        else:
            label = url[last_sep+1:]
        commands = []
        # first try using GIO to get all relevant apps
        if protocol == 'file':
            if not os.path.exists(url):
                return None
            id = url
            apps = mime.get_apps_for_type(mime_type)
            url = shell.quote(url)
            for app in apps:
                cmd = re.sub(r'(%[fFuU])', url, app.get_commandline())
                icon = ''
                if self.show_icons:
                    gicon = app.get_icon()
                    if gicon:
                        if hasattr(gicon, 'get_file'):
                            name = gicon.get_file().get_path()
                        else:
                            name = gicon.get_names()
                    icon = self.icon_finder.find_by_name(name) if gicon else ''
                commands.append({
                    'type': 'application',
                    'label': app.get_name(),
                    'icon': icon,
                    'command': cmd
                })
        else:
            id = href
            app = mime.get_default_for_uri_scheme(protocol)
            if app:
                cmd = re.sub(r'(%[fFuU])', href, app.get_commandline())
                icon = ''
                if self.show_icons:
                    gicon = app.get_icon()
                    icon = self.icon_finder.find_by_name(gicon.get_names()) if gicon else ''
                commands.append({
                    'type': 'application',
                    'label': app.get_name(),
                    'icon': icon,
                    'command': cmd
                })
        # fallback to provided apps
        if not commands:
            apps = el.findall(BOOKMARK_EXPR)
            href = shell.quote(href)
            for app in reversed(apps):
                cmd = re.sub(r'(%[fFuU])', href, app.get('exec').strip('"\''))
                icon = ''
                commands.append({
                    'type': 'application',
                    'label': app.get('name'),
                    'icon': icon,
                    'command': cmd
                })
        icon = self.icon_finder.find_by_mime_type(mime_type) if self.show_icons else ''
        items = [
            {"type": "text", "label": "Open with..."},
            {"type": "separator"}
        ] + commands
        return {
            "type": "menu",
            "id": id,
            "label": label,
            "icon": icon,
            "mimetype": mime_type,
            "items": items
        }

    def create_default(self):
        with open(config.RECENT_FILES_FILE, 'w') as f:
            f.write("""<?xml version="1.0" encoding="UTF-8"?>
<xbel version="1.0"
      xmlns:bookmark="http://www.freedesktop.org/standards/desktop-bookmarks"
      xmlns:mime="http://www.freedesktop.org/standards/shared-mime-info"
>
</xbel>""")
