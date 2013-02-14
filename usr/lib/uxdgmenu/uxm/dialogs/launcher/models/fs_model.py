import os
import locale
from collections import OrderedDict

import gtk
import gio

import uxm.cache as cache
import uxm.icon_finder as icon_finder
import uxm.utils
#import uxm.bench as bench

from . import model
from . import utils

EXCLUDE_SUFFIX = ('.pyc', '~', '.o', '.swp', '.mo')

# Cache up to 32 directories... should be enough
PATH_CACHE = OrderedDict()
PATH_CACHE_SIZE = 32


def listdir(path):
    items = os.listdir(path)
    isdir = os.path.isdir
    join = os.path.join
    isfile = os.path.isfile
    key_func = locale.strxfrm
    dirs = sorted([d for d in items if isdir(join(path, d))], key=key_func)
    files = sorted([f for f in items if isfile(join(path, f))], key=key_func)
    return dirs + files


class FileSystemModel(model.Model):

    def __init__(self):
        super(FileSystemModel, self).__init__()
        if self.use_gtk_theme:
            t = icon_finder.get_gtk_theme()
            if t:
                self.theme = t
        self.cache = cache.open()
        self.icon_finder = icon_finder.IconFinder(
            self.theme, self.icon_size, self.default_icon, self.cache
        )
        self.folder_symlink = self.icon_finder.find_by_mime_type('inode/directory', True)
        self.folder_icon = self.icon_finder.find_by_mime_type('inode/directory', False)

        self.current_search = ""
        self.last_visited = ""
        self.model_filter = self.model.filter_new()
        self.model_filter.set_visible_func(self.search_callback)

    def get_model(self):
        return self.model_filter

    def new_filter(self):
        self.model_filter = self.model.filter_new()
        self.model_filter.set_visible_func(self.search_callback)

    def configure(self):
        self.default_icon = self.prefs.get('Icons', 'application')
        self.icon_size = self.prefs.getint('Icons', 'size')
        self.use_gtk_theme = self.prefs.getboolean('Icons', 'use_gtk_theme')
        self.theme = self.prefs.get('Icons', 'theme')
        self.file_manager = self.prefs.get('General', 'filemanager')
        self.open_cmd = self.prefs.get('General', 'open_cmd')

    def filter(self, filename):
        self.current_search = filename
        self.model_filter.refilter()

    def search_callback(self, mod, it, data=None):
        name = mod.get_value(it, model.COLUMN_NAME)
        if name:
            return name.find(self.current_search) == 0

    def browse(self, dir):
        self.current_search = ""
        # remove the model completely to avoid calling the filter func
        # while adding new rows
        self.new_model()

        path = os.path.realpath(dir)
        if not os.path.isdir(path):
            return False

        # Don't load the same path twice in a row
        if path == self.last_visited:
            return True
        else:
            self.last_visited = path

        if path in PATH_CACHE:
            for column in PATH_CACHE[path]:
                self.model.append(column)
        else:
            if len(PATH_CACHE) >= PATH_CACHE_SIZE:
                PATH_CACHE.popitem(last=False)
            columns = []
            for i, name in enumerate(listdir(path)):
                filepath = os.path.join(path, name)
                if os.path.isdir(filepath):
                    t = model.TYPE_DIR
                    mimetype = uxm.utils.mime.INODE_DIR
                    if os.path.islink(filepath):
                        icon = self.folder_symlink
                    else:
                        icon = self.folder_icon
                elif os.path.isfile(filepath):
                    t = model.TYPE_FILE
                    mimetype = uxm.utils.mime.guess(filepath)
                    icon = self.icon_finder.find_by_mime_type(mimetype)
                icon = utils.load_icon(icon, self.icon_size)
                column = (i, t, name, icon, mimetype)
                columns.append(column)
                self.model.append(column)
            PATH_CACHE[path] = columns
        # recreate the filter
        self.new_filter()

        return True

    def get_action_menu(self, it):
        filename, mimetype = self.model_filter.get(it, model.COLUMN_NAME, model.COLUMN_MIMETYPE)
        filepath = os.path.join(self.last_visited, filename)
        gfile = gio.File(path=filepath)
        menu = gtk.Menu()
        menu.append(gtk.MenuItem('Open with...'))
        menu.append(gtk.SeparatorMenuItem())
        for app_info in gio.app_info_get_all_for_type(mimetype):
            gicon = app_info.get_icon()
            if gicon:
                if hasattr(gicon, 'get_file'):
                    name = gicon.get_file().get_path()
                else:
                    name = gicon.get_names()
            icon = self.icon_finder.find_by_name(name) if gicon else ''
            if icon:
                img = gtk.Image()
                img.set_from_file(icon)
                menuitem = gtk.ImageMenuItem(gtk.STOCK_EXECUTE)
                menuitem.set_image(img)
                menuitem.set_label(app_info.get_name())
            else:
                menuitem = gtk.MenuItem(app_info.get_name())
            menuitem.appinfo = app_info
            menuitem.file = gfile
            menu.append(menuitem)
        return menu
