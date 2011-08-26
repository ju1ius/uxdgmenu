from . import TYPE_FLAT
from .. import base

class Formatter(base.Formatter):

    supports_dynamic_menus = False
    supports_includes = True
    supports_icons = True
    submenus_first = True

    def get_type(self):
        return TYPE_FLAT

    def escape_id(self, id):
        return "uxdgmenu_%s" % id.lower().replace(' ', '_').replace('-', '_')

    def format_rootmenu(self, content):
        return """
%s
local main_menu = awful.menu.new({ items = uxdgmenu_rootmenu })    
""" % content

    def format_menu(self, id, content):
      return """
%s
return %s
""" % (content, self.escape_id(id))

    def format_text_item(self, txt, level=0):
        return self.format_application(
            txt, 'nil', '', level
        )

    def format_include(self, id, filepath, level=0):
        return """local %(id)s = dofile("%(file)s")\n""" % {
            "id": self.escape_id(id),
            "file": filepath.encode('utf-8')
        }

    def format_separator(self, level=0):
        return """  { "--------------------", nil },\n"""

    def format_application(self, name, cmd, icon, level=0):
        return '  { "%s", "%s", "%s" },\n' % (
            name.encode('utf-8'), cmd, icon
        )

    def format_directory(self, id, name, icon, content, level=0):
        return """local %s = {\n%s}\n""" % (
            self.escape_id(id), content
        )

    def format_submenu(self, id, name, icon, submenu, level=0):
        id = self.escape_id(id)
        return '  { "%s", %s, "%s" },\n' % (
            name.encode('utf-8'), id, icon
        )

    def format_wm_menu(self, id, name, icon, level=0):
        return """local %(id)s = {
  { "Manual", "x-terminal-emulator -e 'man awesome'" },
  { "Edit Config", "x-terminal-emulator -e  'nano ~/.config/awesome/rc.lua'" },
  { "Restart", awesome.restart },
  { "Quit", awesome.quit }
}
""" % {
            "id": self.escape_id(id), "i": "  " * level
        }

