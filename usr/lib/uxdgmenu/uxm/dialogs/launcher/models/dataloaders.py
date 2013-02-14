"""
This module will eventually provide loaders for the case where the uxm-daemon
isn't monitoring a specific type of data.
"""
import gio


class DataLoader(object):

    def __init__(self, icon_finder):
        self.icon_finder = icon_finder

    def load(self):
        return []

    def gicon_to_path(self, gicon):
        if gicon:
            if hasattr(gicon, 'get_file'):
                name = gicon.get_file().get_path()
            else:
                name = gicon.get_names()
            return self.icon_finder.find_by_name(name)
        return ""


class AppsLoader(DataLoader):

    def load(self):
        items = []
        for appinfo in gio.app_info_get_all():
            item = {
                'type': 'application',
                'id': appinfo.get_id(),
                'name': appinfo.get_name(),
                'command': appinfo.get_executable(),
                'comment': appinfo.get_description(),
                'icon': self.gicon_to_path(appinfo.get_icon())
            }
            items.append(item)
        return items


class BookmarksLoader(DataLoader):
    pass


class RecentFilesLoader(DataLoader):
    pass
