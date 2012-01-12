import uxm.formatter as base

class Formatter(base.TreeFormatter):

    def format_menu(self, data):
        return "\n".join(self.get_children(data))

    def format_rootmenu(self, data):
        return self.format_menu(data)

    def format_text_item(self, data, level=0):
        return ""

    def format_separator(self, data, level=0):
        return ""

    def format_application(self, data, level=0):
        return '%sprog "%s" %s %s' % (
            self.indent(level),
            data['label'],
            data['icon'] if data['icon'] else '-',
            data['command']
        )

    def format_submenu(self, data, level=0):
        return """%(i)smenu "%(n)s" %(icn)s {
%(items)s
%(i)s}""" % {
                "i": self.indent(level),
                "icn": data['icon'] if data['icon'] else '-',
                "n": data['label'],
                "items": "\n".join(self.get_children(data, level))
            }
