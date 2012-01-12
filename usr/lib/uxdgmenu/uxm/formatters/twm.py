import uxm.formatter as base

class Formatter(base.FlatFormatter):

    def format_rootmenu(self, data):
        return self.format_menu(data)

    def format_menu(self, data):
        return "\n".join(self.get_children(data, False))

    def format_submenu(self, data, entries, level=0):
        return """menu "%s"
{
%s
}
""" % ( data['id'], "\n".join(entries) )

    def format_separator(self, data, level=0):
        return '  "" f.nop' 

    def format_application(self, data, level=0):
        return '  "%s" f.exec "%s &"' % (data['label'], data['command'])

    def format_submenu_entry(self, data, level=0):
        return '  "%s" f.menu "%s"' % (data['label'], data['id'])

    def format_text_item(self, level=0):
        return ""
