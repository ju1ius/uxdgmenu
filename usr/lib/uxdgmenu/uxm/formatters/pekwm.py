from . import base

class Menu(base.TreeMenu):

    supports_icons = False

    def format_menu(self, content):
        return content

    def format_separator(self, level=0):
        indent = "  " * level
        return "%sSeparator{}\n" % indent

    def format_application(self, name, cmd, icon, level=0):
        indent = "  " * level
        return '%sEntry = "%s" { Actions = "Exec %s &" }\n' % (indent, name, cmd)

    def format_submenu(self, id, name, icon, submenu, level=0):
        indent = "  " * level
        return '%sSubmenu = "%s" {\n%s%s}\n' % (indent, name, submenu, indent)
