import uxm.formatter as base

class Formatter(base.FlatFormatter):

    supports_icons = True
    submenus_first = False

    def escape_id(self, id):
        return "uxdgmenu_%s" % id.lower().replace(' ', '_').replace('-', '_')

    def format_rootmenu(self, data):
        return self.format_menu(data)

    def format_menu(self, data):
        return self.format_submenu(data)

    def format_submenu(self, data, level=0):
        return """defmenu("%s",
{
%s
})
""" % (
            self.escape_id(data['id']),
            ",\n".join(self.get_children(data, True))
        )

    def format_separator(self, level=0):
        return '' 

    def format_application(self, data, level=0):
        return """  menuentry("%s", "ioncore.exec_on(_, '%s')")""" % (
            data['label'], data['command']
        )

    def format_submenu_entry(self, data, level=0):
        return '  submenu("%s", "%s")' % (
            self.escape_id(data['id']),
            data['label']
        )

    def format_text_item(self, level=0):
        return ""
