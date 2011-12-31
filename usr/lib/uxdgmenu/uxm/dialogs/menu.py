import os, sys, subprocess

import pygtk
pygtk.require('2.0')
import gtk

import cPickle as pickle
from uxm.formatter import TreeFormatter

class GtkFormatter(TreeFormatter):

    def set_launch_callback(self, cb):
        self.launch_callback = cb

    def _get_item(self, label, icon):
        pixbuf = gtk.gdk.pixbuf_new_from_file(icon)
        ick = gtk.IconSet(pixbuf)
        scaled = ick.render_icon(gtk.Style(), gtk.TEXT_DIR_LTR, gtk.STATE_NORMAL, gtk.ICON_SIZE_LARGE_TOOLBAR, None, None)
        img = gtk.image_new_from_pixbuf(scaled)
        item = gtk.ImageMenuItem(stock_id = label)
        item.set_image(img)
        return item

    def format_menu(self, data, level=0):
        #menu = gtk.MenuItem()
        #for item in self.get_children(data, level):
            #print item
            #menu.append(item)
        #return self.format_submenu(data, 0)
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

    def start(self):
        self.data = self.load_data()
        for i in self.formatter.format_menu(self.data):
            self.append(i)
        self.connect('hide', gtk.main_quit)
        self.show_all()
        self.popup(None, None, None, 0, 0)
        gtk.main()

    def load_data(self):
        f = os.path.expanduser('~/.cache/uxdgmenu/uxm-applications.menu.pckl')
        with open (f, 'r') as fp:
            return pickle.load(fp)

    def exec_command(self, widget, cmd):
        try:
            subprocess.call(cmd)
        finally:
            gtk.main_quit()
