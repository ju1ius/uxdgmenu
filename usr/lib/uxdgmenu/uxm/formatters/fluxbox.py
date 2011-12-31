import os
from uxm.formatter import TreeFormatter

class FluxboxFormatter(TreeFormatter):

    def get_rootmenu_path(self):
        return os.path.expanduser('~/.cache/uxdgmenu/rootmenu.fluxbox')

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
        return "%s[separator] (%s)" % (
            self.indent(level), '-' * 50
        )

    def format_application(self, data, level=0):
        return "%s[exec] (%s) {%s} <%s>" % (
            self.indent(level),
            self.escape_label(data['label']),
            data['command'],
            data['icon']
        )

    def format_submenu(self, data, level=0):
        id = data['id']
        if id == 'uxm-applications':
            return self.format_applications_menu(data, level)
        elif id == 'uxm-bookmarks':
            return self.format_bookmarks_menu(data, level)
        elif id == 'uxm-recently-used':
            return self.format_recently_used_menu(data, level)
        elif id == 'uxm-wm-config':
            return self.format_wm_menu(data, level)
        elif id == 'uxm-menu':
            return self.format_uxm_menu(data, level)

        items = "\n".join(self.get_children(data, level))
        return """%(i)s[submenu] (%(n)s) <%(icn)s>
%(items)s
%(i)s[end]""" % {
            "i": self.indent(level),
            "n": self.escape_label(data['label']),
            "icn": data['icon'],
            "items": items
        }

    def format_applications_menu(self, data, level=0):
        return """%(i)s[submenu] (%(n)s) <%(icn)s>
%(i)s%(i)s[include] (~/.cache/uxdgmenu/uxm-applications.menu.fluxbox)
%(i)s[end]""" % {
            "i": self.indent(level),
            "n": self.escape_label(data['label']),
            "icn": data['icon']
        }

    def format_bookmarks_menu(self, data, level=0):
        return """%(i)s[submenu] (%(n)s) <%(icn)s>
%(i)s%(i)s[include] (~/.cache/uxdgmenu/bookmarks.fluxbox)
%(i)s[end]""" % {
            "i": self.indent(level),
            "n": self.escape_label(data['label']),
            "icn": data['icon']
        }
    def format_recently_used_menu(self, data, level=0):
        return """%(i)s[submenu] (%(n)s) <%(icn)s>
%(i)s%(i)s[include] (~/.cache/uxdgmenu/recently-used.fluxbox)
%(i)s[end]""" % {
            "i": self.indent(level),
            "n": self.escape_label(data['label']),
            "icn": data['icon']
        }

    def format_wm_menu(self, data, level=0):
        return """%(i)s[submenu] (Fluxbox)
%(i)s  [config] (%(conf)s)
%(i)s  [submenu] (%(styles)s)
%(i)s    [stylesdir] (/usr/share/fluxbox/styles)
%(i)s    [stylesdir] (~/.fluxbox/styles)
%(i)s  [end]
%(i)s  [reconfig]
%(i)s  [restart]
%(i)s  [exit]
%(i)s[end]""" % {
            "conf": 'Configuration',
            "styles": 'Themes',
            "i": self.indent(level)
        }

    def format_uxm_menu(self, data, level=0):
        return """%(i)s[submenu] (%(name)s) <%(icon)s>
%(i)s  [exec] (%(update)s) { uxm-daemon update -pa -f fluxbox }
%(i)s  [exec] (%(regen)s) { uxm-daemon generate-rootmenu -pa -f fluxbox }
%(i)s  [exec] (%(clear)s) { uxm-daemon clear-cache -p -f fluxbox }
%(i)s[end]""" % {
            "i": self.indent(level),
            "name": data['label'],
            "icon": data['icon'],
            "update": "Update menus",
            "regen": "Regenerate rootmenu",
            'clear': "Clear cache"
        }

