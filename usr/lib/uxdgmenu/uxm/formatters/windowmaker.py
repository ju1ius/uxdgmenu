from . import base

class Menu(base.TreeMenu):

    supports_icons = False

    def format_menu(self, content):
        return content

    def format_separator(self, level=0):
        return ""

    def format_application(self, name, cmd, icon, level=0):
        indent = "  " * level
        return '%s"%s" EXEC %s\n' % (indent, name, cmd)

    def format_submenu(self, id, name, icon, submenu, level=0):
        indent = "  " * level
        return """%(i)s"%(n)s" MENU\n%(sub)s%(i)s"%(n)s" END\n""" % {
            "i": indent, "n": name, "sub": submenu
        }
