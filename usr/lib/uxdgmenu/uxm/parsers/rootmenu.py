import uxm.parsers.applications as applications

class Parser(applications.Parser):

    def parse_submenu(self, entry, level=1):
        if 'Applications' == entry.get_name():
            return self.parse_applications_menu(entry, level)
        return super(Parser, self).parse_submenu(entry, level)

    def parse_applications_menu(self, entry, level):
        icon = self.icon_finder.find_by_name(entry.get_icon()) if self.show_icons else ''
        return {
            "type": "menu",
            "id": entry.get_name().encode('utf-8'),
            "label": entry.get_display_name().encode('utf-8'),
            "icon": icon.encode('utf-8'),
            "items": []
        }
