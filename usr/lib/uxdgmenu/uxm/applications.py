import os, sys, re
from . import base, adapters, formatters

class ApplicationsMenu(base.Menu):

    def __init__(self, formatter):
        super(ApplicationsMenu, self).__init__(formatter)
        self.adapter = self.get_default_adapter()
        self.filter_debian = os.path.isfile('/usr/bin/update-menus')

    def parse_config(self):
        super(ApplicationsMenu, self).parse_config()
        show_all = self.config.getboolean('Menu', 'show_all')
        if show_all:
            self.show_flags = adapters.SHOW_EMPTY
        self.terminal_emulator = self.config.get('Menu', 'terminal')

    def parse_menu_file(self, menu_file):
        root = self.adapter.get_root_directory(menu_file, self.show_flags)
        return {
            "type": "menu",
            "id": root.get_menu_id(),
            "items": [ i for i in self.parse_directory(root) ]
        }
        #t = self.formatter_type
        #if t == formatters.TYPE_TREE:
            #entries = self.parse_directory(root)
        #elif t == formatters.TYPE_FLAT:
            #entries = self.parse_directory_flat(root)
        #output = "".join( entries )
        #return self.formatter.format_menu(root.get_menu_id(), output)

    def parse_separator(self, entry, level):
        return { "type": "separator" }
        #return self.formatter.format_separator(level)

    def parse_directory(self, entry, level=0):
        for child in entry.get_contents():
            t = child.get_type()
            if t == adapters.TYPE_SEPARATOR:
                yield self.parse_separator(child, level)
            elif t == adapters.TYPE_DIRECTORY:
                yield self.parse_submenu(child, level)
            elif t == adapters.TYPE_ENTRY:
                data = self.parse_application(child, level)
                if data is not None:
                    yield self.parse_application(child, level)

    def parse_directory_flat(self, entry, level=0):
        output= []
        entries = []
        submenus = []
        id = entry.get_menu_id()
        name = entry.get_name()
        icon = self.icon_finder.find_by_name(entry.get_icon()) if self.show_icons else ''
        add_submenus = submenus.extend
        add_entry = entries.extend
        for e in entry.get_contents():
            t = e.get_type()
            if t == adapters.TYPE_DIRECTORY:
                add_submenus( self.parse_directory_flat(e, level) )
        for e in entry.get_contents():
            t = e.get_type()
            if t == adapters.TYPE_SEPARATOR:
                add_entry( self.parse_separator(e, level) )
            elif t == adapters.TYPE_ENTRY:
                add_entry( self.parse_application(e, level) )
            elif t == adapters.TYPE_DIRECTORY:
                add_entry( self.parse_submenu_flat(e, level) )
        entries = "".join(entries)
        if not self.formatter.submenus_first:
            output.append(
                self.formatter.format_directory(id, name, icon, entries, level)
            )
        output.extend(submenus)
        if self.formatter.submenus_first:
            output.append(
                self.formatter.format_directory(id, name, icon, entries, level)
            )
        return output

    def parse_submenu(self, entry, level):
        id = entry.get_menu_id()
        name = entry.get_name()
        icon = self.icon_finder.find_by_name(entry.get_icon()) if self.show_icons else ''
        return {
            "type": "menu",
            "id": id,
            "label": name,
            "icon": icon,
            "items": [ i for i in self.parse_directory(entry) ]
        }
        #submenu = "".join( self.parse_directory(entry, level+1) )
        #return self.formatter.format_submenu(id, name, icon, submenu, level)

    def parse_submenu_flat(self, entry, level):
        id = entry.get_menu_id()
        name = entry.get_name()
        icon = self.icon_finder.find_by_name(entry.get_icon()) if self.show_icons else ''
        return self.formatter.format_submenu(id, name, icon, level)

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
            "label": name,
            "command": cmd,
            "icon": icon
        }
        #return self.formatter.format_application(name, cmd, icon, level)

    def get_default_adapter(self):
       return adapters.get_default_adapter()

    def get_adapter(self):
        return self.adapter

    def set_adapter(self, name):
        self.adapter = adapters.get_adapter(name)
