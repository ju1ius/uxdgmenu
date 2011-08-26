from . import base

class Menu(base.FlatMenu):

    supports_icons = True
    submenus_first = False

    def format_menu(self,content):
        return content

    def format_directory(self, id, name, icon, entries, level):
        return """menu "%s"\n{\n%s}\n""" % ( name, entries )

    def format_separator(self, indent):
        return '  "" f.nop\n' 

    def format_application(self, name, cmd, icon, indent):
        return '  "%s" f.exec "%s &"\n' % (name, cmd)

    def format_submenu(self, id, name, icon, indent):
        return '  "%s" f.menu "%s"\n' % (name, name)

