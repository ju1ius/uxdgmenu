import re
from . import config, cache, icon_finder

class BaseParser(object):

    def __init__(self):
        self.config = config.get()
        self.parse_config()
        self.exe_regex = re.compile(r' [^ ]*%[fFuUdDnNickvm]')
        if self.show_icons:
            if self.use_gtk_theme:
                t = icon_finder.get_gtk_theme()
                if t: self.theme = t
            self.cache = cache.Cache()
            self.cache.open()
            self.icon_finder = icon_finder.IconFinder(
                self.theme, self.icon_size, self.default_icon, self.cache
            )

    def __del__(self):
        if self.show_icons:
            self.cache.close()

    def parse_config(self):
        show_icons = self.config.getboolean('Icons', 'show')
        self.show_icons = show_icons
        if self.show_icons:
            self.default_icon = self.config.get('Icons', 'default')
            self.icon_size = self.config.getint('Icons', 'size')
            self.use_gtk_theme = self.config.getboolean('Icons', 'use_gtk_theme')
            self.theme = self.config.get('Icons','theme')
