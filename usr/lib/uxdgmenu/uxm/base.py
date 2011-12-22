import os, sys, stat, re
from abc import ABCMeta, abstractmethod
import xdg.IconTheme as IconTheme
from . import config, cache, icon_finder, formatters

class Menu(object):

    def __init__(self, formatter):
        if isinstance(formatter, str):
            self.formatter = formatters.get_formatter(formatter)
        else:
            self.formatter = formatter
        self.formatter_type = self.formatter.get_type()
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
        self.show_icons = show_icons and self.formatter.supports_icons
        if self.show_icons:
            self.default_icon = self.config.get('Icons', 'default')
            self.icon_size = self.config.getint('Icons', 'size')
            self.use_gtk_theme = self.config.getboolean('Icons', 'use_gtk_theme')
            self.theme = self.config.get('Icons','theme')

def _formatter_error(method):
    raise NotImplementedError(
        "Subclasses of uxm.base.Formatter must implement a %s method" % method
    )

class Formatter(object):

    #supports_dynamic_menus = False"
    #supports_includes = False
    #supports_icons = False

    def get_name(self):
        return self.__module__.split('.')[-1]

    def get_type(self):
        _formatter_error("get_type")

    def format_rootmenu(self, content):
        _formatter_error("format_rootmenu")

    def format_menu(self, id, content):
        _formatter_error("format_menu")

    def format_text_item(self, txt, level=0):
        _formatter_error("format_text_item")

    def format_separator(self, level=0):
        _formatter_error("format_separator")

    def format_application(self, name, cmd, icon, level=0):
        _formatter_error("format_application")

    def format_submenu(self, id, name, icon, submenu, level=0):
        _formatter_error("format_submenu")
