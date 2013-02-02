import os
import re

import uxm.parser as parser
import uxm.config as config
from uxm.utils import shell
from uxm.utils import fs
from uxm.utils import mime

_ = config.translate


class Parser(parser.BaseParser):

    def __init__(self, formatter="pckl", path='uxm-places'):
        super(Parser, self).__init__()
        self.command = path
        self.formatter = formatter
        self.file_manager = self.preferences.get('General', 'filemanager')
        self.folder_icon = ''
        if self.show_icons:
            self.folder_icon = self.icon_finder.find_by_mime_type('inode/directory')

    def parse_path(self, path):
        fm = self.file_manager
        fi = self.folder_icon
        items = [
            {
                "type": "application",
                "label": "%s..." % _("Open"),
                "icon": fi,
                "command": '%s %s' % (fm, shell.quote(path))
            },
            {"type": "separator"}
        ]
        append = items.append
        files = fs.listdir(path, True)
        for filename in files:
            if filename.startswith('.') or filename.endswith('~'):
                continue
            filepath = os.path.join(path, filename)
            if os.path.isfile(filepath):
                icon = self.icon_finder.find_by_file_path(filepath) if self.show_icons else ''
                mimetype = mime.guess(filepath)
                apps = self.get_applications(shell.quote(filepath), mimetype)
                item = {
                    "type": "menu",
                    "id": filepath,
                    "label": filename,
                    "icon": icon,
                    "mimetype": mimetype,
                    "items": apps
                }
            else:
                cmd = '%s -f "%s" %s' % (
                    self.command, self.formatter, shell.quote(filepath)
                )
                item = {
                    "type": "menu",
                    "id": filepath,
                    "label": filename,
                    "icon": fi,
                    "items": [],
                    "command": cmd
                }
            append(item)
        result = {
            "type": "menu",
            "label": "Places",
            "id": "uxm-places",
            "items": items
        }
        return result

    def get_applications(self, path, mimetype):
        apps = mime.get_apps_for_type(mimetype)
        commands = [
            {'type': 'text', 'label': 'Open with...'},
            {'type': 'separator'}
        ]
        for app in apps:
            cmd = re.sub(r'(%[fFuU])', path, app.get_commandline())
            icon = ''
            if self.show_icons:
                gicon = app.get_icon()
                if gicon:
                    if hasattr(gicon, 'get_file'):
                        name = gicon.get_file().get_path()
                    else:
                        name = gicon.get_names()
                icon = self.icon_finder.find_by_name(name) if gicon else ''
            commands.append({
                'type': 'application',
                'label': app.get_name(),
                'icon': icon,
                'command': cmd
            })
        return commands
