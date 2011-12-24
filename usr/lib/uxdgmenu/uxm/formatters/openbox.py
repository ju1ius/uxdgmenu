from . import base
from xml.sax.saxutils import escape, quoteattr

class Formatter(base.TreeFormatter):

    supports_dynamic_menus = True
    supports_includes = False
    supports_icons = True

    def format_rootmenu(self, content):
        return """<?xml version="1.0" encoding="UTF-8"?>
<openbox_menu xmlns="http://openbox.org/"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://openbox.org/
                file:///usr/share/openbox/menu.xsd">

<menu id="root-menu" label="Openbox 3">
%s
</menu>
</openbox_menu>""" % content

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
            "i": self.indent(level), "id": quoteattr(id), "n": quoteattr(label),
            "cmd": quoteattr(cmd), "icn": quoteattr(icon)
        }

    def format_separator(self, level=0):
        return "%s<separator/>" % (self.indent(level))

    def format_submenu(self, data, level=0):
        submenu = "\n".join(self.get_children(data, level+1))
        return """%(i)s<menu id=%(id)s label=%(n)s icon=%(icn)s>
%(sub)s
%(i)s</menu>""" % {
            "i": self.indent(level), "id": quoteattr(data['id']),
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

    def format_wm_menu(self, id, name, icon, level=0):
        return """%(i)s<menu id=%(name)s label=%(icon)s>
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
%(i)s</menu>
""" % {
            "name": quoteattr(name), "icon": quoteattr(icon),
            "i": self.indent(level)
        }

