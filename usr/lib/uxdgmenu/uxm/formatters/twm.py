from . import base

class Formatter(base.FlatFormatter):

    def format_menu(self, data):
        return "\n".join(self.get_children(data, False))

    def format_submenu(self, data, entries, level):
        return """menu "%s"
{
%s
}
""" % ( data['label'], "\n".join(entries) )

    def format_separator(self, data, indent):
        return '  "" f.nop' 

    def format_application(self, data, indent):
        return '  "%s" f.exec "%s &"' % (data['label'], data['command'])

    def format_submenu_entry(self, data, indent):
        return '  "%s" f.menu "%s"' % (data['label'], data['id'])

