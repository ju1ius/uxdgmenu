import json
from . import base

class Formatter(base.TreeFormatter):

    def escape_label(self, label):
        return label.replace('"', '\\"')

    def format_rootmenu(self, data):
        return self.format_submenu(data, 0)

    def format_menu(self, data):
      return json.dumps(data)

    def format_text_item(self, data, level=0):
        return """%s{ "type": "text", "label": "%s" }""" % (
            self.indent(level),
            self.escape_label(data['label'])
        )

    def format_include(self, data, level=0):
        return """%s{ "type": "include", "file": "%s" }""" % (
            self.indent(level),
            self.escape_label(data['file'])
        )

    def format_separator(self, data, level=0):
        return '%s{ "type": "separator" }' % (self.indent(level))

    def format_application(self, data, level=0):
        return """%s{ "type": "application", "label": "%s", "command": "%s", "icon": "%s" }""" % (
            self.indent(level), self.escape_label(data['label']),
            data['command'],
            data['icon']
        )

    def format_submenu(self, data, level=0):
        items = ",\n".join(self.get_children(data, level+1))
        return """%(i)s{
%(i)s  "type": "menu",
%(i)s  "label": "%(n)s",
%(i)s  "icon": "%(icn)s",
%(i)s  "items": [
%(items)s
%(i)s  ]
%(i)s}""" % {
            "i": self.indent(level),
            "n": self.escape_label(data['label']),
            "icn": data['icon'],
            "items": items
        }

    def format_wm_menu(self, data, level=0):
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
            "name": data['name'], "icon": data['icon'],
            "conf": 'Configuration',
            "styles": 'Themes',
            "i": self.indent(level)
        }
