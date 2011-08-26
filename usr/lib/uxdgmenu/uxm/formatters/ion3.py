from . import base

class Menu(base.FlatMenu):

    supports_icons = True
    submenus_first = False

    def format_menu(self,content):
        return content

    def format_directory(self, id, name, icon, entries, level):
        return """defmenu("%s",
{
%s})
""" % ( name, entries )

    def format_separator(self, level=0):
        return '' 

    def format_application(self, name, cmd, icon, level=0):
        return '  menuentry("%s", "ioncore.exec_on(_, \'%s\')"),\n' % (name, cmd)

    def format_submenu(self, id, name, icon, level=0):
        return '  submenu("%s", "%s"),\n' % (name, name)

