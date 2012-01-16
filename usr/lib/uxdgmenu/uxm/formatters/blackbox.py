from uxm.formatter import TreeFormatter
import uxm.config as config

class Formatter(TreeFormatter):

    def __init__(self):
        super(Formatter, self).__init__()
        self.config = config.get()
        self.apps_as_submenu = self.config.get('Applications', 'as_submenu')

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

    def format_include(self, filename, data, level=0):
        return "%s[include] (%s)" % (
            self.indent(level),
            self.escape_label(filename)
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
        id = data['id']
        if id == 'uxm-applications':
            return self.format_applications_menu(data, level)
        elif id == 'uxm-bookmarks':
            return self.format_bookmarks_menu(data, level)
        elif id == 'uxm-recent-files':
            return self.format_recent_files_menu(data, level)
        elif id == 'uxm-devices':
            return self.format_recent_files_menu(data, level)
        elif id == 'uxm-wm-config':
            return self.format_wm_menu(data, level)
        elif id == 'uxm-menu':
            return self.format_uxm_menu(data, level)

        items = "\n".join(self.get_children(data, level))
        return """%(i)s[submenu] (%(n)s)
%(items)s
%(i)s[end]""" % {
            "i": self.indent(level),
            "n": self.escape_label(data['label']),
            "items": items
        }

    def format_applications_menu(self, data, level=0):
        cache = "%s/applications.blackbox" % config.CACHE_DIR
        include = self.format_include(cache, data)
        if not self.apps_as_submenu:
            return include
        return self.format_include_submenu(cache, data, level)

    def format_bookmarks_menu(self, data, level=0):
        cache = "%s/bookmarks.blackbox" % config.CACHE_DIR
        return self.format_include_submenu(cache, data, level)

    def format_recent_files_menu(self, data, level=0):
        cache = "%s/recent-files.blackbox" % config.CACHE_DIR
        return self.format_include_submenu(cache, data, level)

    def format_devices_menu(self, data, level=0):
        cache = "%s/devices.blackbox" % config.CACHE_DIR
        return self.format_include_submenu(cache, data, level)

    def format_include_submenu(self, filepath, data, level=0):
        return """%(i)s[submenu] (%(n)s)
%(i)s%(i)s[include] (%(menu))
%(i)s[end]""" % {
            "i": self.indent(level),
            "n": self.escape_label(data['label']),
            "menu": filepath
        }

    def format_wm_menu(self, data, level=0):
        return """%(i)s[submenu] (%(name)s)
%(i)s  [config] (%(conf)s)
%(i)s  [submenu] (%(styles)s)
%(i)s    [stylesdir] (/usr/share/blackbox/styles)
%(i)s    [stylesdir] (~/.blackbox/styles)
%(i)s  [end]
%(i)s  [reconfig]
%(i)s  [restart]
%(i)s  [exit]
%(i)s[end]
""" % {
            "name": data['label'],
            "conf": 'Configuration',
            "styles": 'Themes',
            "i": self.indent(level)
        }

    def format_uxm_menu(self, data, level=0):
        return """%(i)s[submenu] (%(name)s)
%(i)s  [exec] (%(update)s) { uxm-daemon update -p -f fluxbox }
%(i)s  [exec] (%(regen)s) { uxm-daemon update:rootmenu -p -f fluxbox }
%(i)s  [exec] (%(clear)s) { uxm-daemon clear:cache -p -f fluxbox }
%(i)s[end]""" % {
            "i": self.indent(level),
            "name": data['label'],
            "update": "Update menus",
            "regen": "Regenerate rootmenu",
            'clear': "Clear cache"
        }



