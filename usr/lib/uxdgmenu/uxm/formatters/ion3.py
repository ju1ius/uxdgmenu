import uxm.formatter as base

class Formatter(base.FlatFormatter):

    def escape_id(self, id):
        return "uxdgmenu_%s" % id.lower().replace(' ', '_').replace('-', '_')

    def format_rootmenu(self, data):
        return self.format_menu(data)

    def format_menu(self, data):
        entries = self.get_children(data, True)
        return ",\n".join(entries)


    def format_submenu(self, data, entries, level=0):
        return """defmenu("%s",
{
%s
})""" % (
            self.escape_id(data['id']),
            ",\n".join(entries)
        )

    def format_separator(self, data, level=0):
        return """  menuentry("", nil)"""

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
