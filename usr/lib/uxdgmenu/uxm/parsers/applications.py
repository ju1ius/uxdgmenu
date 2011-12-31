import os, sys, re
from .. import parser, adapters

class Parser(parser.BaseParser):

    def __init__(self):
        super(Parser, self).__init__()
        self.adapter = self.get_default_adapter()
        self.filter_debian = os.path.isfile('/usr/bin/update-menus')

    def parse_config(self):
        super(Parser, self).parse_config()
        show_all = self.config.getboolean('Menu', 'show_all')
        if show_all:
            self.show_flags = adapters.SHOW_EMPTY
        self.terminal_emulator = self.config.get('Menu', 'terminal')

    def parse_menu_file(self, menu_file):
        root = self.adapter.get_root_directory(menu_file, self.show_flags)
        return {
            "type": "menu",
            "id": root.get_menu_id().encode('utf-8'),
            "items": [ i for i in self.parse_directory(root) ]
        }

    def parse_separator(self, entry, level):
        return { "type": "separator" }

    def parse_directory(self, entry, level=0):
        for child in entry.get_contents():
            t = child.get_type()
            if t == adapters.TYPE_SEPARATOR:
                yield self.parse_separator(child, level)
            elif t == adapters.TYPE_DIRECTORY:
                yield self.parse_submenu(child, level)
            elif t == adapters.TYPE_ENTRY:
                data = self.parse_application(child, level)
                if data is not None: yield data

    def parse_submenu(self, entry, level):
        id = entry.get_menu_id()
        name = entry.get_name()
        icon = self.icon_finder.find_by_name(entry.get_icon()) if self.show_icons else ''
        return {
            "type": "menu",
            "id": id.encode('utf-8'),
            "label": name.encode('utf-8'),
            "icon": icon.encode('utf-8'),
            "items": [ i for i in self.parse_directory(entry) ]
        }

    def parse_application(self, entry, level):
        # Skip Debian specific menu entries
        filepath = entry.get_desktop_file_path()
        if self.filter_debian and "/.local/share/applications/menu-xdg/" in filepath:
            return None
        # Escape entry name
        name = entry.get_display_name()
        # Strip command arguments
        cmd = self.exe_regex.sub('', entry.get_exec())
        if entry.get_launch_in_terminal():
            cmd = self.terminal_emulator % {"title": name, "command": cmd}
        # Get icon
        icon = self.icon_finder.find_by_name(entry.get_icon()) if self.show_icons else ''

        return {
            "type": "application",
            "label": name.encode('utf-8'),
            "command": cmd.encode('utf-8'),
            "icon": icon.encode('utf-8')
        }

    def get_default_adapter(self):
       return adapters.get_default_adapter()

    def get_adapter(self):
        return self.adapter

    def set_adapter(self, name):
        self.adapter = adapters.get_adapter(name)
