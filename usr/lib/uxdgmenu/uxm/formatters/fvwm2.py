import uxm.formatter as base

class Formatter(base.FlatFormatter):

    def format_rootmenu(self, data):
        return self.format_menu(data)

    def format_menu(self, data):
        entries = self.get_children(data, True)
        return """
%s
""" % ( "\n".join(entries) )

    def format_text_item(self, level=0):
        return ""

    def format_submenu(self, data, entries, level=0):
        icon = "%%(icn)s%" % data['icon'] if data['icon'] else ''
        return """DestroyMenu "uxdgmenu-%(id)s"
AddToMenu "uxdgmenu-%(id)s" "%(n)s" Title
%(items)s
""" % { 
            "id": data['id'],
            "n": data['label'],
            "items": "\n".join(entries)
        }

    def format_separator(self, data, level=0):
        return ""

    def format_application(self, data, level=0):
        return '+       "%s%s" Exec %s' % (
            data['label'],
            "%%(icn)s%" % data['icon'] if data['icon'] else '',
            data['command']
        )

    def format_submenu_entry(self, data, level=0):
        icon = 
        return '+       "%s%s" Popup %s\n' % (
            data['label'],
            "%%(icn)s%" % data['icon'] if data['icon'] else '',
            data['id']
        )

