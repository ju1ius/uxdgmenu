from . import base

class Formatter(base.FlatFormatter):

    supports_dynamic_menus = False
    supports_includes = True
    supports_icons = True

    def escape_id(self, id):
        return "uxdgmenu_%s" % id.lower().replace(' ', '_').replace('-', '_')

    def format_rootmenu(self, content):
        return """
%s
local main_menu = awful.menu.new({ items = uxdgmenu_rootmenu })    
""" % content

    def format_menu(self, data):
        entries = self.get_children(data, True)
        return """
%s
return %s
""" % (
        "\n".join(entries),
        self.escape_id(data['id'])
    )

    def format_text_item(self, data, level=0):
        return self.format_application(
            data['label'].encode('utf-8'), 'nil', '', level
        )

    def format_include(self, data, level=0):
        return """local %(id)s = dofile("%(file)s")""" % {
            "id": self.escape_id(data['id']),
            "file": data['file'].encode('utf-8')
        }

    def format_separator(self, data, level=0):
        return """  { "--------------------", nil }"""

    def format_application(self, data, level=0):
        return '  { "%s", "%s", "%s" }' % (
            data['label'].encode('utf-8'), data['command'], data['icon']
        )

    def format_submenu(self, data, entries, level=0):
        return """local %s = {
%s
}""" % (
            self.escape_id(data['id']), ",\n".join(entries)
        )

    def format_submenu_entry(self, data, level=0):
        return '  { "%s", %s, "%s" }' % (
            data['label'].encode('utf-8'),
            self.escape_id(data['id']),
            data['icon']
        )

    def format_wm_menu(self, data, level=0):
        return """local %(id)s = {
  { "Manual", "x-terminal-emulator -e 'man awesome'" },
  { "Edit Config", "x-terminal-emulator -e  'nano ~/.config/awesome/rc.lua'" },
  { "Restart", awesome.restart },
  { "Quit", awesome.quit }
}
""" % {
            "id": self.escape_id(data['id'])
        }

