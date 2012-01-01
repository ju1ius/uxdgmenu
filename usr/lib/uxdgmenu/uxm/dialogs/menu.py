import os, sys, shlex, subprocess

import pygtk
pygtk.require('2.0')
import gtk

import cPickle as pickle

import uxm.parsers.places
from uxm.formatter import TreeFormatter
import uxm.dialogs.error

class GtkFormatter(TreeFormatter):

    def set_launch_callback(self, cb):
        self.launch_callback = cb

    def _get_item(self, label, icon):
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
        self.formatter = GtkFormatter()
        self.formatter.set_launch_callback(self.exec_command)
        self.places_parser = uxm.parsers.places.Parser()
        self.path_cache = {}

    def start(self):
        self.load_menu()
        self.connect('hide', gtk.main_quit)
        self.show_all()
        self.popup(None, None, None, 0, 0)
        gtk.main()

    def load_menu(self):
        data = self.load_data('~/.cache/uxdgmenu/rootmenu.pckl')
        for item in self.formatter.format_menu(data):
            name = item.get_name()
            if name == 'uxm-applications':
                self.load_submenu(item, '~/.cache/uxdgmenu/applications.pckl')
            elif name == 'uxm-bookmarks':
                self.load_submenu(item, '~/.cache/uxdgmenu/bookmarks.pckl')
                self.load_places_menu()
            elif name == 'uxm-recently-used':
                self.load_submenu(item, '~/.cache/uxdgmenu/recently-used.pckl')
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

        editor = gtk.ImageMenuItem(gtk.STOCK_PROPERTIES)
        editor.connect("activate", self.exec_command, "uxm-editor")
        submenu.append(editor)

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
            d = uxm.dialogs.error.Dialog(str(e))
        finally:
            gtk.main_quit()
