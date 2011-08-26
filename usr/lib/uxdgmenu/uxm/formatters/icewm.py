from . import base

class Menu(base.TreeMenu):

    supports_icons = True

    def format_menu(self, content):
        return content

    def format_separator(self, level=0):
        return ""

    def format_application(self, name, cmd, icon, level=0):
        if not icon: icon = '-'
        indent = "  " * level
        return '%sprog "%s" %s %s\n' % (indent, name, icon, cmd)

    def format_submenu(self, id, name, icon, submenu, level=0):
        if not icon: icon = '-'
        indent = "  " * level
        return '%smenu "%s" %s {\n%s%s}\n' % (indent, name, icon, submenu, indent)
