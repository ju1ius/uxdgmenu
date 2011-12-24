import os, xdg.Mime
from . import base
from .. import utils

class Parser(base.Parser):

    def __init__(self):
        super(Parser, self).__init__()
        if not self.formatter.supports_dynamic_menus:
            wm = self.formatter.get_name()
            assert self.formatter.supports_dynamic_menus, \
                "%s window manager doesn't support dynamic menus" % wm.title()

    def parse_config(self):
        super(Parser, self).parse_config()
        self.file_manager = self.config.get('Menu', 'filemanager')
        self.open_cmd = self.config.get('Menu', 'open_cmd')
    
    def parse_path(self, path):
        fm = self.file_manager
        open_cmd = self.open_cmd
        folder_icon = self.icon_finder.find_by_mime_type('inode/directory') if self.show_icons else ''
        folder_icon = folder_icon.encode('utf-8')
        items = [
            {
                "type": "application",
                "label": "Browse here...",
                "icon": folder_icon
                "command": '%s "%s"' % (fm, path)
            },
            { "type": "separator" }
        ]
        append = items.append
        files = utils.sorted_listdir(path, show_files)
        for filename in files:
            if filename.startswith('.') or filename.endswith('~'):
                continue
            filepath = os.path.join(path, filename)
            if os.path.isfile(filepath):
                icon = self.icon_finder.find_by_file_path(filepath) if self.show_icons else ''
                cmd = '%s "%s"' % (open_cmd, filepath)
                item = {
                    "type": "application",
                    "label": filename.encode('utf-8'),
                    "icon": icon.encode('utf-8'),
                    "command": cmd.encode('utf-8')
                }
            else:
                cmd = 'uxm-places -f "%s" "%s" "%s"' % (fm, wm, filepath)
                item = {
                    "type": "pipemenu",
                    "id": filepath.encode('utf-8'),
                    "label": filename.encode('utf-8'),
                    "icon": folder_icon
                    "command": cmd.encode('utf-8')
                }
            append(item)
        return {
            "type": "menu",
            "label": "Places",
            "id": "uxm-places",
            "items": items
        }
