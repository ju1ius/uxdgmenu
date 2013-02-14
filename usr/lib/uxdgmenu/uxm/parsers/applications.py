import os

import uxm.parser as parser
import uxm.adapters as adapters
import uxm.utils.shell


class Parser(parser.BaseParser):

    def __init__(self):
        super(Parser, self).__init__()
        self.adapter = self.get_default_adapter()
        self.filter_debian = os.path.isfile('/usr/bin/update-menus')

    def parse_config(self):
        super(Parser, self).parse_config()
        self.show_all = self.preferences.getboolean('Applications', 'show_all')
        self.terminal_emulator = self.preferences.get('General', 'terminal')

    def parse_menu_file(self, menu_file):
        root = self.adapter.parse(menu_file, self.show_all)
        return {
            "type": "menu",
            "id": root.get_name().encode('utf-8'),
            "label": root.get_display_name().encode('utf8'),
            "items": [i for i in self.parse_directory(root)]
        }

    def parse_separator(self, entry, level):
        return {"type": "separator"}

    def parse_directory(self, entry, level=0):
        for child in entry:
            t = child.get_type()
            if t == adapters.TYPE_SEPARATOR:
                yield self.parse_separator(child, level)
            elif t == adapters.TYPE_DIRECTORY:
                yield self.parse_submenu(child, level)
            elif t == adapters.TYPE_ENTRY:
                data = self.parse_application(child, level)
                if data is not None:
                    yield data

    def parse_submenu(self, entry, level):
        icon = self.icon_finder.find_by_name(entry.get_icon()) if self.show_icons else ''
        return {
            "type": "menu",
            "id": entry.get_name().encode('utf-8'),
            "label": entry.get_display_name().encode('utf-8'),
            "icon": icon.encode('utf-8'),
            "items": [i for i in self.parse_directory(entry)]
        }

    def parse_application(self, entry, level):
        # Skip Debian specific menu entries
        filepath = entry.get_filename()
        if self.filter_debian and "/.local/share/applications/menu-xdg/" in filepath:
            return None
        # Strip command arguments
        cmd = uxm.utils.shell.clean_exec(entry.get_exec())
        if entry.is_terminal():
            cmd = '%s -e "%s"' % (self.terminal_emulator, cmd)
        # Get icon
        icon = self.icon_finder.find_by_name(entry.get_icon()) if self.show_icons else ''

        return {
            "type": "application",
            "label": entry.get_display_name().encode('utf-8'),
            "command": cmd.encode('utf-8'),
            "icon": icon.encode('utf-8')
        }

    def get_default_adapter(self):
        return adapters.get_default_adapter()

    def get_adapter(self):
        return self.adapter

    def set_adapter(self, name):
        self.adapter = adapters.get_adapter(name)
