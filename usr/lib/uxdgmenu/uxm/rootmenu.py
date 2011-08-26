import os
from . import config, applications, formatters
from .adapters import SHOW_EMPTY
        
import gettext
__t = gettext.translation("fluxdgmenu", "/usr/share/locale")
_ = __t.ugettext      

class RootMenu(applications.ApplicationsMenu):

    def parse_config(self):
        super(RootMenu, self).parse_config()
        self.as_submenu = self.config.getboolean("Menu", "as_submenu")

    def parse_menu_file(self, menu_file):
        root = self.adapter.get_root_directory(menu_file, SHOW_EMPTY)
        t = self.formatter_type
        if t == formatters.TYPE_TREE:
            entries = self.parse_directory(root, 1)
        elif t == formatters.TYPE_FLAT:
            entries = self.parse_directory_flat(root, 1)
        output = "".join( entries )
        return self.formatter.format_rootmenu(output)

    def parse_submenu(self, entry, level=1):
        id = entry.get_menu_id()
        if id == 'uxm-applications':
            return self.parse_applications_menu(entry, level)
        if id == 'uxm-bookmarks':
            return self.parse_bookmarks_menu(entry, level)
        if id == 'uxm-recently-used':
            return self.parse_recently_used_menu(entry, level)
        elif id == 'uxm-custom-entries':
            return self.parse_custom_entries(entry, level)
        elif id == 'uxm-menu':
            return self.parse_uxm_menu(entry, level)
        elif id == 'uxm-wm-config':
            return self.parse_wm_menu(entry, level)
        return super(RootMenu, self).parse_submenu(entry, level)

    def parse_directory_flat(self, entry, level=1):
        id = entry.get_menu_id()
        if id == 'uxm-applications':
            return self.parse_applications_menu(entry, level)
        if id == 'uxm-bookmarks':
            return self.parse_bookmarks_menu(entry, level)
        if id == 'uxm-recently-used':
            return self.parse_recently_used_menu(entry, level)
        elif id == 'uxm-custom-entries':
            return self.parse_custom_entries(entry, level)
        elif id == 'uxm-menu':
            return self.parse_uxm_menu(entry, level)
        elif id == 'uxm-wm-config':
            return self.parse_wm_menu(entry, level)
        return super(RootMenu, self).parse_directory_flat(entry, level)

    def parse_applications_menu(self, entry, level):
        id = entry.get_menu_id()
        name = entry.get_name()
        icon = self.icon_finder.find_by_name(entry.get_icon()) if self.show_icons else ''
        if self.formatter.supports_includes:
            filename = self.get_menu_cache_file('applications')
            if self.formatter_type == formatters.TYPE_FLAT or not self.as_submenu:
                return self.formatter.format_include(id, filename, 0)
            else:
                return self.formatter.format_submenu(
                    'uxm-applications', name, icon,
                    self.formatter.format_include(id, filename, level+1),
                    level
                )
        elif self.formatter.supports_dynamic_menus:
            return self.formatter.format_dynamic_menu(
                'uxm-applications', name, self.get_show_cmd('applications'),
                icon, level+1        
            )

    def parse_bookmarks_menu(self, entry, level):
        id = entry.get_menu_id()
        name = entry.get_name()
        icon = self.icon_finder.find_by_name(entry.get_icon()) if self.show_icons else ''
        if self.formatter.supports_includes:
            filename = self.get_menu_cache_file('bookmarks')
            if self.formatter_type == formatters.TYPE_FLAT:
                return self.formatter.format_include(id, filename, 0)
            else:
                return self.formatter.format_submenu(
                    'uxm-applications', name, icon,
                    self.formatter.format_include(id, filename, level+1),
                    level
                )
            #return self.formatter.format_include(id, filename, level+1)
        elif self.formatter.supports_dynamic_menus:
            return self.formatter.format_dynamic_menu(
                'uxm-bookmarks', name, self.get_show_cmd('bookmarks'),
                icon, level+1
            )

    def parse_recently_used_menu(self, entry, level):
        id = entry.get_menu_id()
        name = entry.get_name()
        icon = self.icon_finder.find_by_name(entry.get_icon()) if self.show_icons else ''
        if self.formatter.supports_includes:
            filename = self.get_menu_cache_file('recently-used')
            if self.formatter_type == formatters.TYPE_FLAT:
                return self.formatter.format_include(id, filename, 0)
            else:
                return self.formatter.format_submenu(
                    'uxm-applications', name, icon,
                    self.formatter.format_include(id, filename, level+1),
                    level
                )
        elif self.formatter.supports_dynamic_menus:
            return self.formatter.format_dynamic_menu(
                'uxm-recently-used', name, self.get_show_cmd('recently-used'),
                icon, level+1
            )

    def parse_uxm_menu(self, entry, level):
        id = entry.get_menu_id()
        update_cmd = self.formatter.format_application(
            _("Update"), "uxm-daemon update --all --progress", '', level+1
        )
        generate_cmd = self.formatter.format_application(
            _("Generate"), "uxm-daemon generate-rootmenu --progress",
            '', level+1
        )
        if self.formatter_type == formatters.TYPE_FLAT:
            return self.formatter.format_directory(
                'uxm-menu', _("Menu"), '',
                update_cmd + generate_cmd, 0
            )
        else:
            return self.formatter.format_submenu(
                'uxm-menu', _("Menu"), '',
                update_cmd + generate_cmd, level
            )

    def parse_custom_entries(self, entry, level):
        id = entry.get_menu_id()
        return self.get_custom_entries()

    def parse_wm_menu(self, entry, level):
        id = entry.get_menu_id()
        name = entry.get_name()
        icon = self.icon_finder.find_by_name(entry.get_icon()) if self.show_icons else ''
        return self.formatter.format_wm_menu('uxm-wm-menu', name, icon, level)

    def get_menu_cache_file(self, menu):
        filename = "%s-%s" % (self.formatter.get_name(), menu)
        return os.path.join(config.CACHE_DIR, filename)

    def get_show_cmd(self, menu):
        return "uxm-daemon -w %s show %s" % (self.formatter.get_name(), menu)

    def get_custom_entries(self):
        filename = "%s-custom-entries" % self.formatter.get_name()
        f = os.path.join(config.CONFIG_DIR, filename)
        entries = ''
        with open(f, 'r') as fp:
            entries = fp.read()
        return entries
