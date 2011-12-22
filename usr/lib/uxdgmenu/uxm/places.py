import os, xdg.Mime
from . import base, utils

class PlacesMenu(base.Menu):

    def __init__(self, formatter):
        super(PlacesMenu, self).__init__(formatter)
        if not self.formatter.supports_dynamic_menus:
            wm = self.formatter.get_name()
            assert self.formatter.supports_dynamic_menus, \
                "%s window manager doesn't support dynamic menus" % wm.title()

    def parse_config(self):
        super(PlacesMenu, self).parse_config()
        self.file_manager = self.config.get('Menu', 'filemanager')
        self.open_cmd = self.config.get('Menu', 'open_cmd')
    
    def parse_path(self, path):
        fm = self.file_manager
        open_cmd = self.open_cmd
        folder_icon = self.icon_finder.find_by_mime_type('inode/directory') if self.show_icons else ''
        output = [
            self.formatter.format_application(
                'Browse Here...', '%s "%s"' % (fm, path),
                folder_icon, 1
            ),
            self.formatter.format_separator(1)
        ]
        append = output.append
        files = utils.sorted_listdir(path, show_files)
        for filename in files:
            if filename.startswith('.') or filename.endswith('~'):
                continue
            filepath = os.path.join(path, filename)
            if os.path.isfile(filepath):
                icon = self.icon_finder.find_by_file_path(filepath) if self.show_icons else ''
                cmd = "%s %s" % (open_cmd, filepath)
                item = self.formatter.format_application(filename, cmd, icon, 1)
            else:
                cmd = 'uxm-places -f "%s" "%s" "%s"' % (fm, wm, filepath)
                item = self.formatter.format_dynamic_menu(
                    filepath, filename, cmd, folder_icon, 1
                )
            append(item)
        return self.formatter.format_menu("places", "".join(output) )

