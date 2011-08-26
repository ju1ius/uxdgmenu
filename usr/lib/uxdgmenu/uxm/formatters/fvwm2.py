from . import base

class Menu(base.FlatMenu):

    supports_icons = True

    def format_menu(self,content):
        return content

    def format_directory(self, id, name, icon, entries, level=0):
        icon = "%"+ icon +"%" if icon else ''
        return """DestroyMenu "uxdgmenu-%(id)s"
AddToMenu "uxdgmenu-%(id)s" "%(n)s" Title
%(e)s
""" % { "id": id, "n": name, "e": entries }

    def format_separator(self, level=0):
        return ""

    def format_application(self, name, cmd, icon, level=0):
        icon = "%"+ icon +"%" if icon else ''
        return '+       "%s%s" Exec %s\n' % (name, icon, cmd)

    def format_submenu(self, id, name, icon, level=0):
        icon = "%"+ icon +"%" if icon else ''
        return '+       "%s%s" Popup %s\n' % (name, icon, id)

