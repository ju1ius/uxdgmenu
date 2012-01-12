from uxm.formatter import TreeFormatter

class Formatter(TreeFormatter):

    def escape_label(self, label):
        return label.replace('(', ':: ').replace(')', ' ::')

    def format_rootmenu(self, data):
        contents = "\n".join(self.get_children(data))
        return """[begin]
%s
[end]""" % contents

    def format_menu(self, data):
      return "\n".join(self.get_children(data))

    def format_text_item(self, data, level=0):
        return "%s[nop] (%s)" % (
            self.indent(level),
            self.escape_label(data['label'])
        )

    def format_include(self, data, level=0):
        return "%s[include] (%s)" % (
            self.indent(level),
            self.escape_label(data['file'])
        )

    def format_separator(self, data, level=0):
        return "%s[separator] (---------------------)" % (self.indent(level))

    def format_application(self, data, level=0):
        return "%s[exec] (%s) {%s}" % (
            self.indent(level),
            self.escape_label(data['label']),
            data['command']
        )

    def format_submenu(self, data, level=0):
        items = "\n".join(self.get_children(data, level))
        return """%(i)s[submenu] (%(n)s)
%(items)s
%(i)s[end]""" % {
            "i": self.indent(level),
            "n": self.escape_label(data['label']),
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
            "name": data['label'], "icon": data['icon'],
            "conf": 'Configuration',
            "styles": 'Themes',
            "i": self.indent(level)
        }



