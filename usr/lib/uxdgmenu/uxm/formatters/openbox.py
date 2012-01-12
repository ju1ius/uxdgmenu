from xml.sax.saxutils import escape, quoteattr

import uxm.formatter
import uxm.config as config

class OpenboxFormatter(uxm.formatter.TreeFormatter):

    def get_rootmenu_path(self):
        return "~/.config/openbox/menu.xml"

    def format_rootmenu(self, data):
        output = "\n".join(self.get_children(data))
        return """<?xml version="1.0" encoding="UTF-8"?>
<openbox_menu
    xmlns="http://openbox.org/"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://openbox.org/
                        file:///usr/share/openbox/menu.xsd"
>
<menu id="root-menu" label="Openbox 3">
%s
</menu>
</openbox_menu>""" % output

    def format_menu(self, data):
        output = "\n".join(self.get_children(data))
        return """<?xml version="1.0" encoding="UTF-8"?>
<openbox_pipe_menu>
%s
</openbox_pipe_menu>""" % output

    def format_text_item(self, data, level=0):
        return "%s<item label=%s />" % (self.indent(level), quoteattr(data['label']))

    def format_pipemenu(self, data, level=0):
        return "%(i)s<menu id=%(id)s label=%(n)s execute=%(cmd)s icon=%(icn)s/>" % {
            "i": self.indent(level),
            "id": quoteattr(data['id']),
            "n": quoteattr(data['label']),
            "cmd": quoteattr(data['command']),
            "icn": quoteattr(data['icon'])
        }

    def format_separator(self, data, level=0):
        return "%s<separator/>" % (self.indent(level))

    def format_submenu(self, data, level=0):
        id = data['id']
        if id == 'uxm-applications':
            data['command'] = "cat %s/uxm-applications.menu.openbox" % (
                config.CACHE_DIR)
            return self.format_pipemenu(data, level)
        elif id == 'uxm-bookmarks':
            data['command'] = "cat %s/bookmarks.openbox" % (
                config.CACHE_DIR)
            return self.format_pipemenu(data, level)
        elif id == 'uxm-recent-files':
            data['command'] = "cat %s/recent-files.openbox" % (
                config.CACHE_DIR)
            return self.format_pipemenu(data, level)
        elif id == 'uxm-wm-config':
            return self.format_wm_menu(data, level)
        elif id == 'uxm-menu':
            return self.format_uxm_menu(data, level)
        elif id == 'uxm-places':
            data['command'] = "uxm-places -f openbox ~"
            return self.format_pipemenu(data, level)
        elif 'command' in data:
            return self.format_pipemenu(data, level)

        submenu = "\n".join(self.get_children(data, level+1))
        return """%(i)s<menu id=%(id)s label=%(n)s icon=%(icn)s>
%(sub)s
%(i)s</menu>""" % {
            "i": self.indent(level), "id": quoteattr(id),
            "n": quoteattr(data['label']),
            "icn": quoteattr(data['icon']), "sub": submenu
        }

    def format_application(self, data, level=0):
        return """%(i)s<item label=%(n)s icon=%(icn)s>
%(i)s  <action name='Execute'>
%(i)s    <command>%(c)s</command>
%(i)s  </action>
%(i)s</item>""" % {
            "i": self.indent(level), "n": quoteattr(data['label']),
            "icn": quoteattr(data['icon']), "c": escape(data['command'])
        }

    def format_wm_menu(self, data, level=0):
        return """<menu id="client-list-menu" />
%(i)s<menu id="ob-conf" label="Openbox">
%(i)s  <item label="ObConf">
%(i)s    <action name="Execute">
%(i)s      <execute>obconf</execute>
%(i)s    </action>
%(i)s  </item>
%(i)s  <item label="Reconfigure">
%(i)s    <action name="Reconfigure" />
%(i)s  </item>
%(i)s  <item label="Restart">
%(i)s    <action name="Restart" />
%(i)s  </item>
%(i)s  <item label="Exit">
%(i)s    <action name="Exit" />
%(i)s  </item>
%(i)s</menu>""" % {
            "i": self.indent(level)
        }

    def format_uxm_menu(self, data, level=0):
        return """%(i)s<menu id=%(name)s label=%(icon)s>
%(i)s  <item label="%(update)s">
%(i)s    <action name="Execute">
%(i)s      <execute>uxm-daemon update -p -f openbox</execute>
%(i)s    </action>
%(i)s  </item>
%(i)s  <item label="%(regen)s">
%(i)s    <action name="Execute">
%(i)s      <execute>uxm-daemon update:rootmenu -p -f openbox</execute>
%(i)s    </action>
%(i)s  </item>
%(i)s  <item label="%(clear)s">
%(i)s    <action name="Execute">
%(i)s      <execute>uxm-daemon clear:cache -p -f openbox</execute>
%(i)s    </action>
%(i)s  </item>
%(i)s</menu>""" % {
            "i": self.indent(level),
            "name": data['label'],
            "icon": data['icon'],
            "update": "Update menus",
            "regen": "Regenerate rootmenu",
            'clear': "Clear cache"
        }
