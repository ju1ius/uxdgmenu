import uxm.formatter as base

class Formatter(base.TreeFormatter):

    def format_rootmenu(self, data):
        return self.format_menu(data)

    def format_menu(self, data):
        return "\n".join(self.get_children(data))

    def format_separator(self, data, level=0):
        return ""

    def format_text_item(self, data, level=0):
        return ""

    def format_application(self, data, level=0):
        return '%s"%s" EXEC %s' % (
            self.indent(level), data['label'], data['command']
        )

    def format_submenu(self, data, level=0):
        return """%(i)s"%(n)s" MENU
%(items)s
%(i)s"%(n)s" END
""" % {
            "i": self.indent(level),
            "n": data['label'],
            "items": "\n".join(self.get_children(data, level))
        }
