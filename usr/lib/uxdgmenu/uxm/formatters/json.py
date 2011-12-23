from . import TYPE_TREE
from .. import base

class Formatter(base.Formatter):

    supports_dynamic_menus = False
    supports_includes = False
    supports_icons = True

    def get_type(self):
        return TYPE_TREE

    def escape_label(self, label):
        return label.replace('"', '\\"')

    def format_rootmenu(self, content):
        return """{
  "type": "menu",
  "items": [
%s
  ]
}\n""" % content

    def format_menu(self, id, content):
      return content

    def format_text_item(self, txt, level=0):
        return """%s{ "type": "text", "label": "%s" }\n""" % (
            "  " * level,
            self.escape_label(txt.encode('utf-8'))
        )

    def format_include(self, filepath, level=0):
        return """%s{ "type": "include", "file": "%s" }\n""" % (
            "  " * level,
            self.escape_label(filepath.encode('utf-8'))
        )

    def format_separator(self, level=0):
        return '%s{ "type": "separator" }\n' % ("  " * level)

    def format_application(self, name, cmd, icon, level=0):
        return '%s{ "type": "application", "label": "%s", "command": "%s", "icon": "%s" },\n' % (
            "  " * level, self.escape_label(name.encode('utf-8')),
            cmd.encode('utf-8'),
            icon.encode('utf-8')
        )

    def format_submenu(self, id, name, icon, submenu, level=0):
        return """%(i)s{
  "type": "menu",
  "label": "%(n)s",
  "icon": "%(icn)s",
  "items": [
%(sub)s%(i)s  ]
%(i)s}\n""" % {
            "i": "  " * level,
            "n": self.escape_label(name.encode('utf-8')),
            "icn": icon.encode('utf-8'),
            "sub": submenu
        }

    def format_wm_menu(self, id, name, icon, level=0):
        return """%(i)s[submenu] (%(name)s) <%(icon)s>
%(i)s  [config] (%(conf)s)
%(i)s  [submenu] (%(styles)s)
%(i)s    [stylesdir] (/usr/share/fluxbox/styles)
%(i)s    [stylesdir] (~/.fluxbox/styles)
%(i)s  [end]
%(i)s  [reconfig]
%(i)s  [restart]
%(i)s  [exit]
%(i)s[end]
""" % {
            "name": name, "icon": icon,
            "conf": 'Configuration',
            "styles": 'Themes',
            "i": "  " * level
        }
