import os, shlex, subprocess

import pygtk
pygtk.require('2.0')
import gtk

import cPickle as pickle

import uxm.config as config
import uxm.parsers.places
from uxm.formatter import TreeFormatter
import uxm.dialogs.error


ROOT_MENU =   '%s.pckl' % config.ROOTMENU_CACHE
APPS_MENU =   '%s.pckl' % config.APPS_CACHE
BOOK_MENU =   '%s.pckl' % config.BOOKMARKS_CACHE
RECENT_MENU = '%s.pckl' % config.RECENT_FILES_CACHE
DEVICES_MENU ='%s.pckl' % config.DEVICES_CACHE

def clear_cache():
    for f in [ROOT_MENU, APPS_MENU, BOOK_MENU, RECENT_MENU]:
        if os.path.exists(f):
            try:
                os.remove(f)
            except OSError, why:
                uxm.dialogs.error.Dialog(why)


class GtkFormatter(TreeFormatter):

    def set_launch_callback(self, cb):
        self.launch_callback = cb

    def _get_item(self, label, icon):
        try:
            pixbuf = gtk.gdk.pixbuf_new_from_file(icon)
            ick = gtk.IconSet(pixbuf)
            scaled = ick.render_icon(
                gtk.Style(),
                gtk.TEXT_DIR_LTR, gtk.STATE_NORMAL,
                gtk.ICON_SIZE_MENU, None, None
            )
            img = gtk.image_new_from_pixbuf(scaled)
            item = gtk.ImageMenuItem(stock_id = label)
            item.set_image(img)
        except:
            # Icon not found
            item = gtk.MenuItem(label = label)
        return item

    def format_menu(self, data, level=0):
        return [i for i in self.get_children(data, level)]

    def format_application(self, data, level=0):
        # Icon
        item = self._get_item(data['label'], data['icon'])
        item.connect("activate", self.launch_callback, data['command'])
        item.show()
        return item

    def format_submenu(self, data, level=0):
        # Icon
        item = self._get_item(data['label'], data['icon'])
        item.set_name(data['id'])
        submenu = gtk.Menu()
        for child in self.get_children(data, level):
            submenu.append(child) 
        item.set_submenu(submenu)
        item.show()
        return item
   
    def format_separator(self, data, level=0):
        return gtk.SeparatorMenuItem()

    def format_rootmenu(self, data, level=0):
        pass
    def format_text_item(self, data, level=0):
        pass
    def format_include(self, data, level=0):
        pass
    def format_wm_menu(self, data, level=0):
        pass


class Menu(gtk.Menu):


    def __init__(self):
        super(Menu, self).__init__()
        self.standalone = False
        self.apps_menu_file = config.MENU_FILE

        self.preferences = config.preferences()
        self.apps_as_submenu = self.preferences.getboolean('Applications', 'as_submenu')

        self.formatter = GtkFormatter()
        self.formatter.set_launch_callback(self.exec_command)
        self.places_parser = uxm.parsers.places.Parser()
        self.path_cache = {}

    def set_applications_menu_file(self,filename):
        self.apps_menu_file = filename

    def open(self):
        gtk.gdk.threads_init()
        gtk.gdk.threads_enter()
        self.check_paths()
        self.load_menu()
        self.connect('hide', self.on_hide)
        self.show_all()
        self.popup(None, None, None, 0, 0)

    def main(self):
        self.standalone = True
        self.open()
        gtk.main()
        gtk.gdk.threads_leave()

    def close(self):
        self.popdown()
        if self.standalone:
            gtk.main_quit()
        gtk.gdk.threads_leave()

    def on_hide(self, widget, data=None):
        self.close()

    def load_menu(self):
        data = self.load_data(ROOT_MENU)
        for item in self.formatter.format_menu(data):
            name = item.get_name()
            if name == 'uxm-applications':
                if self.apps_as_submenu:
                    self.load_submenu(item, APPS_MENU)
                else:
                    data = self.load_data(APPS_MENU)
                    apps = self.formatter.format_menu(data)
                    for a in apps[0:-1]:
                        self.append(a)
                    item = apps[-1]
            elif name == 'uxm-bookmarks':
                self.load_submenu(item, BOOK_MENU)
                self.load_places_menu()
            elif name == 'uxm-recent-files':
                self.load_submenu(item, RECENT_MENU)
            elif name == 'uxm-devices':
                self.load_submenu(item, DEVICES_MENU)
            elif name == 'uxm-menu':
                self.load_uxm_menu(item)
            elif name == 'uxm-wm-config':
                # We don't want it here, so we
                continue
            self.append(item)

    def load_data(self, filepath):
        f = os.path.expanduser(filepath)
        with open (f, 'r') as fp:
            return pickle.load(fp)

    def load_submenu(self, widget, filepath):
        data = self.load_data(filepath)
        submenu = gtk.Menu()
        for item in self.formatter.format_menu(data):
            submenu.append(item)
        widget.set_submenu(submenu)
    
    def load_uxm_menu(self, widget):
        submenu = gtk.Menu()

        update = gtk.ImageMenuItem(gtk.STOCK_REFRESH)
        update.connect("activate", self.exec_command, "uxm-daemon update:all -p")
        submenu.append(update)

        clear =  gtk.ImageMenuItem(gtk.STOCK_CLEAR)
        clear.connect("activate", self.exec_command, "uxm-daemon clear:cache -p")
        submenu.append(clear)

        submenu.append(gtk.SeparatorMenuItem())

        config = gtk.ImageMenuItem(gtk.STOCK_PREFERENCES)
        config.connect("activate", self.exec_command, "uxm-config")
        submenu.append(config)

        widget.set_submenu(submenu)

    def load_places_menu(self):
        item = gtk.ImageMenuItem(gtk.STOCK_HOME)
        item.set_submenu(gtk.Menu())
        item.connect("activate", self.on_places_activate)
        self.append(item)

    def on_places_activate(self, widget, data=None):
        path = widget.get_name()
        if path == 'GtkImageMenuItem':
            path = os.path.expanduser("~")
        if path in self.path_cache:
            widget.set_submenu(self.path_cache[path])
        data = self.places_parser.parse_path(path)
        submenu = gtk.Menu()
        for item in self.formatter.format_menu(data):
            item.connect("activate", self.on_places_activate)
            submenu.append(item)
        self.path_cache[path] = submenu
        widget.set_submenu(submenu)

    def exec_command(self, widget, cmd):
        try:
            subprocess.call(shlex.split(cmd))
        except Exception, e:
            uxm.dialogs.error.Dialog(str(e))
        finally:
            self.close()

    def check_paths(self):
        generate = False
        for f in [ROOT_MENU, APPS_MENU, BOOK_MENU, RECENT_MENU]:
            if not os.path.exists(f):
                generate = True
                break
        if generate:
            import uxm.daemon as daemon
            import uxm.dialogs.progress as progress
            class Options:
                formatter = 'pckl'
                menu_file = self.apps_menu_file
            progress.indeterminate(
                "Generating menus", daemon.update_all, Options()
            )
