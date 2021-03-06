import uxm.config as config
import uxm.cache as cache
import uxm.icon_finder as icon_finder   

class BaseParser(object):

    def __init__(self):
        self.preferences = config.preferences()
        self.parse_config()
        if self.show_icons:
            if self.use_gtk_theme:
                t = icon_finder.get_gtk_theme()
                if t: self.theme = t
            self.cache = cache.Cache().open()
            self.icon_finder = icon_finder.IconFinder(
                self.theme, self.icon_size, self.default_icon, self.cache
            )

    def __del__(self):
        if self.show_icons:
            self.cache.close()

    def parse_config(self):
        show_icons = self.preferences.getboolean('Icons', 'show')
        self.show_icons = show_icons
        if self.show_icons:
            self.default_icon = self.preferences.get('Icons', 'application')
            self.icon_size = self.preferences.getint('Icons', 'size')
            self.use_gtk_theme = self.preferences.getboolean('Icons', 'use_gtk_theme')
            self.theme = self.preferences.get('Icons','theme')
