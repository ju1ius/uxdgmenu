import os
from collections import OrderedDict
import gtk

from .constants import *
import uxm.utils as utils
import uxm.config as config
import uxm.cache as cache
import uxm.icon_finder as icon_finder   


EXCLUDE_SUFFIX = ('.pyc', '~', '.o', '.swp', '.mo')

# Cache up to 32 directories... should be enough
PATH_CACHE = OrderedDict()
PATH_CACHE_SIZE = 32

class PathFinder(object):

    def __init__(self):
        self.configure()
        if self.use_gtk_theme:
            t = icon_finder.get_gtk_theme()
            if t: self.theme = t
        self.cache = cache.open()
        self.icon_finder = icon_finder.IconFinder(
            self.theme, self.icon_size, self.default_icon, self.cache
        )
        self.folder_symlink = self.icon_finder.find_by_mime_type('inode/directory', True)
        self.folder_icon = self.icon_finder.find_by_mime_type('inode/directory', False)

        self.model = gtk.ListStore(*COLUMNS)
        self.current_search = ""
        self.model_filter = self.model.filter_new()
        self.model_filter.set_visible_func(self.search_callback)

    def configure(self):
        self.prefs = config.preferences()
        self.default_icon = self.prefs.get('Icons', 'application')
        self.icon_size = self.prefs.getint('Icons', 'size')
        self.use_gtk_theme = self.prefs.getboolean('Icons', 'use_gtk_theme')
        self.theme = self.prefs.get('Icons','theme')
        self.file_manager = self.prefs.get('General', 'filemanager')
        self.open_cmd = self.prefs.get('General', 'open_cmd')

    def filter(self, filename):
        self.current_search = filename
        print "searching for", filename
        self.model_filter.refilter()

    def search_callback(self, model, it, data=None):
        name = model.get_value(it, COLUMN_NAME)
        if name:
            return name.find(self.current_search) == 0

    def browse(self, dir):
        print "browsing", dir
        self.current_search = ""
        self.model.clear()

        path = os.path.realpath(dir)
        if not os.path.isdir(path):
            return False

        if path in PATH_CACHE:
            for column in PATH_CACHE[path]:
                self.model.append(column)
        else:
            if len(PATH_CACHE) >= PATH_CACHE_SIZE:
                PATH_CACHE.popitem(last=False)
            columns = []
            for i, name in enumerate(utils.sorted_listdir(path)):
                filepath = os.path.join(path, name)
                if os.path.isdir(filepath):
                    t = TYPE_DIR
                    if os.path.islink(filepath):
                        icon = self.folder_symlink
                    else:
                        icon = self.folder_icon
                elif os.path.isfile(filepath):
                    t = TYPE_FILE
                    icon = self.icon_finder.find_by_file_path(filepath)
                icon = load_icon(icon, self.icon_size)
                column = (i, t, name, icon)
                columns.append(column)
                self.model.append(column)
            PATH_CACHE[path] = columns
            #self.cache.save()

        return True
