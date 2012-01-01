import os, xdg.Mime
from .. import utils, parser

class Parser(parser.BaseParser):

    def __init__(self, formatter="pckl"):
        super(Parser, self).__init__()
        self.formatter = formatter
        self.file_manager = self.config.get('Menu', 'filemanager')
        self.open_cmd = self.config.get('Menu', 'open_cmd')
        self.folder_icon = ''
        if self.show_icons:
            self.folder_icon = self.icon_finder.find_by_mime_type('inode/directory').encode('utf-8')
    
    def parse_path(self, path):
        fm = self.file_manager
        open_cmd = self.open_cmd
        fi = self.folder_icon
        items = [
            {
                "type": "application",
                "label": "Browse here...",
                "icon": fi,
                "command": '%s "%s"' % (fm, path)
            },
            { "type": "separator" }
        ]
        append = items.append
        files = utils.sorted_listdir(path, True)
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
                cmd = 'uxm-places -f "%s" "%s"' % (self.formatter, filepath)
                item = {
                    "type": "menu",
                    "id": filepath.encode('utf-8'),
                    "label": filename.encode('utf-8'),
                    "icon": fi,
                    "items": [],
                    "command": cmd.encode('utf-8')
                }
            append(item)
        result = {
            "type": "menu",
            "label": "Places",
            "id": "uxm-places",
            "items": items
        }
        return result
