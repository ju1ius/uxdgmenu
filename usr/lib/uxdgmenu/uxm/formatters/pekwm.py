import uxm.formatter as base

class Formatter(base.TreeFormatter):

    def format_rootmenu(self, data):
        return self.format_menu(data)

    def format_menu(self, content):
        return "\n".join(self.get_children(data))

    def format_separator(self, data, level=0):
        return "%sSeparator{}" % self.indent(level)

    def format_application(self, data, level=0):
        return '%sEntry = "%s" { Actions = "Exec %s &" }' % (
            self.indent(level),
            data['label'],
            data['command']
        )

    def format_submenu(self, data, level=0):
        indent = self.indent(level)
        return """%(i)sSubmenu = "%(n)s" {
%(items)s
%(i)s}""" % {
                "i": self.indent(level),
                "n": data['label'],
                "items": "\n".join(self.get_children(data, level+1))
            }

    def format_text_item(self, level=0):
        return ""
