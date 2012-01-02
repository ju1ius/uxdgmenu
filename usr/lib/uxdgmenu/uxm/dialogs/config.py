import os

import pygtk
pygtk.require('2.0')
import gtk, gobject

import uxm.config as config
import uxm.utils as utils

class ConfigEditor(object):

    def __init__(self):
        self._load_ui()
        self._load_config()
        self.builder.connect_signals(self)

    def _load_ui(self):
        builder = gtk.Builder()
        builder.add_from_file(
            os.path.join(os.path.dirname(__file__), "uxm-config.glade")
        )
        self.window = builder.get_object('main_window')
        self.save_btn = builder.get_object('save_btn')
        self.save_btn.set_sensitive(False)
        self.close_btn = builder.get_object('close_btn')

        # General
        self.filemanager_entry = builder.get_object('filemanager_entry')
        self.filemanager_chooser_btn = builder.get_object('filemanager_chooser_btn')
        self.filemanager_chooser_btn.set_current_folder('/usr/bin')

        self.terminal_entry = builder.get_object('terminal_entry')
        self.terminal_chooser_btn = builder.get_object('terminal_chooser_btn')
        self.terminal_chooser_btn.set_current_folder('/usr/bin')

        # Icons
        self.icons_show_cb = builder.get_object('icons_show_cb')

        self.icons_size_select = builder.get_object('icons_size_select')
        m = gtk.ListStore(gobject.TYPE_INT)
        m.append([16])
        m.append([24])
        m.append([32])
        m.append([48])
        self.icons_size_select.set_model(m)
        cell = gtk.CellRendererText()
        self.icons_size_select.pack_start(cell, True)
        self.icons_size_select.add_attribute(cell, 'text', 0)

        self.use_gtk_theme_cb = builder.get_object('use_gtk_theme_cb')
        self.icons_theme_entry = builder.get_object('icons_theme_entry')
        # ----- defaults
        self.icons_default_app_entry = builder.get_object('icons_default_app_entry')
        self.icons_default_folder_entry = builder.get_object('icons_default_folder_entry')
        self.icons_default_file_entry = builder.get_object('icons_default_file_entry')
        self.icons_default_bookmark_entry = builder.get_object('icons_default_bookmark_entry')
        
        # Menus
        # ----- applications
        self.menus_apps_show_all_cb = builder.get_object('menus_apps_show_all_cb')
        self.menus_apps_as_submenu_cb = builder.get_object('menus_apps_as_submenu_cb')
        # ----- bookmarks'
        # ----- recent
        self.menus_recent_files_max_items_btn = builder.get_object('menus_recent_files_max_items_btn')
        self.menus_recent_files_max_items_btn.set_adjustment(
            gtk.Adjustment(0, 0, 100, 1)        
        )
        # ----- places
        self.menus_places_show_files_cb = builder.get_object('menus_places_show_files_cb')
        #
        self.builder = builder

    def _load_config(self):
        self.config = config.get()
        # General
        self.filemanager_entry.set_text(
            self.config.get('General', 'filemanager')            
        )
        self.terminal_entry.set_text(
            self.config.get('General', 'terminal')            
        )
        # Icons
        self.icons_show_cb.set_active(
            self.config.getboolean('Icons', 'show')        
        )
        # get icon size
        s = self.config.getint('Icons', 'size')
        if s < 16: s = 16
        # round to the nearest multiple of 8
        icon_size = utils.round_base(s, 8)
        # compute index
        self.icons_size_select.set_active((icon_size / 8) - 2)

        self.use_gtk_theme_cb.set_active(
            self.config.getboolean('Icons', 'use_gtk_theme')        
        )
        self.icons_theme_entry.set_text(
            self.config.get('Icons', 'theme')        
        )
        self.icons_theme_entry.set_sensitive(
            not self.use_gtk_theme_cb.get_active()
        )
        # ----- defaults
        self.icons_default_app_entry.set_text(
            self.config.get('Icons', 'application')        
        )
        self.icons_default_folder_entry.set_text(
            self.config.get('Icons', 'folder')        
        )
        self.icons_default_file_entry.set_text(
            self.config.get('Icons', 'file')        
        )
        self.icons_default_bookmark_entry.set_text(
            self.config.get('Icons', 'bookmark')        
        )
        # Menus
        # ----- apps
        self.menus_apps_show_all_cb.set_active(
            self.config.getboolean('Applications', 'show_all')        
        )
        self.menus_apps_as_submenu_cb.set_active(
            self.config.getboolean('Applications', 'as_submenu')        
        )
        # ----- recent
        self.menus_recent_files_max_items_btn.set_value(
            self.config.getint('Recently Used', 'max_items')        
        )
        # ----- places
        self.menus_places_show_files_cb.set_active(
            self.config.getboolean('Places', 'show_files')        
        )

    def _gather_data(self):
        # General
        fm = self.filemanager_entry.get_text()
        self.config.set('General', 'filemanager', fm)
        term = self.terminal_entry.get_text()
        self.config.set('General', 'terminal', term)
        # Icons
        show_icons = self.icons_show_cb.get_active()
        self.config.set('Icons', 'show', show_icons)
        idx = self.icons_size_select.get_active()
        self.config.set('Icons', 'size', (idx + 2) * 8)
        use_gtk_theme = self.use_gtk_theme_cb.get_active()
        self.config.set('Icons', 'use_gtk_theme', use_gtk_theme)
        theme = self.icons_theme_entry.get_text()
        self.config.set('Icons', 'theme', theme)
        # ----- defaults
        app_icon = self.icons_default_app_entry.get_text()
        self.config.set('Icons', 'application', app_icon)
        folder_icon = self.icons_default_folder_entry.get_text()
        self.config.set('Icons', 'folder', folder_icon)
        file_icon = self.icons_default_file_entry.get_text()
        self.config.set('Icons', 'file', file_icon)
        bk_icon = self.icons_default_bookmark_entry.get_text()
        self.config.set('Icons', 'bookmark', bk_icon)
        # Menus
        # ----- apps
        show_all = self.menus_apps_show_all_cb.get_active()
        self.config.set('Applications', 'show_all', show_all)
        as_submenu = self.menus_apps_as_submenu_cb.get_active()
        self.config.set('Applications', 'as_submenu', as_submenu)
        # ----- recent
        max_items = self.menus_recent_files_max_items_btn.get_value()
        self.config.set('Recently Used', 'max_items', max_items)
        # ----- places
        show_files = self.menus_places_show_files_cb.get_active()
        self.config.set('Places', 'show_files', show_files)

    def start(self):
        self.window.show_all()
        gtk.main()

    # ---------- Signal handlers ---------- #

    def on_destroy(self, widget, data=None):
        gtk.main_quit()

    def on_changed(self, widget, data=None):
        self.save_btn.set_sensitive(True)

    def on_use_gtk_theme_cb_toggled(self, widget, data=None):
        self.icons_theme_entry.set_sensitive(
            not widget.get_active()
        )

    def on_terminal_chooser_btn_file_set(self, widget, data=None):
        self.terminal_entry.set_text(widget.get_filename())

    def on_filemanager_chooser_btn_file_set(self, widget, data=None):
        self.filemanager_entry.set_text(widget.get_filename())

    def on_save(self, widget, data=None):
        self._gather_data()
        with open(config.USER_CONFIG_FILE, 'w') as fp:
            self.config.write(fp)
            self.save_btn.set_sensitive(False)
