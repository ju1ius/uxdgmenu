
from xml.sax.saxutils import escape, quoteattr

class Formatter():

    supports_dynamic_menus = True
    supports_includes = False
    supports_icons = True


    def get_type(self):
        return TYPE_TREE

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
        children = []
        for item in data['items']:
            if item['type'] == 'application':
                children.append( self.format_application(item, 1) )
            elif item['type'] == 'separator':
                children.append( self.format_separator(1) )
            elif item['type'] == 'menu':
                children.append( self.format_submenu(item, 1) )
            elif item['type'] == 'text':
                children.append( self.format_text_item(item, 1) )
        output = "\n".join(children)
        return """<?xml version="1.0" encoding="UTF-8"?>
<openbox_pipe_menu>
%s
</openbox_pipe_menu>""" % output

    def format_text_item(self, data, level=0):
        indent = "  " * level
        return "%s<item label=%s />" % (indent, quoteattr(data['label']))

    def format_dynamic_menu(self, id, label, cmd, icon, level=0):
        return "%(i)s<menu id=%(id)s label=%(n)s execute=%(cmd)s icon=%(icn)s/>\n" % {
            "i": "  " * level, "id": quoteattr(id), "n": quoteattr(label),
            "cmd": quoteattr(cmd), "icn": quoteattr(icon)
        }

    def format_separator(self, level=0):
        return "%s<separator/>" % ("  " * level)

    def format_submenu(self, data, level=0):
        children = []
        for item in data['items']:
            if item['type'] == 'application':
                children.append( self.format_application(item, level+1) )
            elif item['type'] == 'separator':
                children.append( self.format_separator(level+1) )
            elif item['type'] == 'menu':
                children.append( self.format_submenu(item, level+1) )
            elif item['type'] == 'text':
                children.append( self.format_text_item(item, level+1) )
        submenu = "\n".join(children)
        return """%(i)s<menu id=%(id)s label=%(n)s icon=%(icn)s>
%(sub)s
%(i)s</menu>""" % {
            "i": "  " * level, "id": quoteattr(data['id']),
            "n": quoteattr(data['label'].encode('utf-8')),
            "icn": quoteattr(data['icon']), "sub": submenu
        }

    def format_application(self, data, level=0):
        return """%(i)s<item label=%(n)s icon=%(icn)s>
%(i)s  <action name='Execute'>
%(i)s    <command>%(c)s</command>
%(i)s  </action>
%(i)s</item>""" % {
            "i": "  " * level, "n": quoteattr(data['label'].encode('utf-8')),
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
            "i": "  " * level
        }

