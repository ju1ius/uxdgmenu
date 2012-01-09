import os, glob, threading

import pygtk
pygtk.require('2.0')
import gtk, gobject

import uxm.config as config
import uxm.utils as utils
import uxm.dialogs.progress as progress
import uxm.daemon as daemon
import uxm.dialogs.menu

class Options(object):
    """Mock OptionsParser options"""
    def __init__(self, **kwargs):
        for prop, val in kwargs.iteritems():
            self.__dict__[prop] = val

class ComboBoxTextDecorator(object):
    """Decorator for simple text comboboxes"""
    def __init__(self, cb):
        self.cb = cb
        self.model = gtk.ListStore(gobject.TYPE_STRING)
        self.cb.set_model(self.model)
        cell = gtk.CellRendererText()
        self.cb.pack_start(cell, True)
        self.cb.add_attribute(cell, 'text', 0)

    def append_text(self, text):
        self.model.append([str(text)])

    def get_active_text(self):
        i = self.cb.get_active()
        row = self.model[i]
        return row[0]

    def set_active(self, idx):
        self.cb.set_active(idx)

class DaemonStatusMonitor(threading.Thread, gobject.GObject):
    __gsignals__ = {
        "status-change": (
            gobject.SIGNAL_RUN_LAST,
            gobject.TYPE_NONE,
            (gobject.TYPE_BOOLEAN,)
        )
    }

    def __init__(self):
        threading.Thread.__init__(self)
        gobject.GObject.__init__(self)

        self.stopevent = threading.Event()
        self.status = False

    def run(self):
        while not self.stopevent.isSet():
            pids = utils.pgrep('uxdgmenud', exact=True, user=os.environ['USER'])
            if pids:
                if self.status is False:
                    self.emit('status-change', True)
                    self.status = True
            else:
                if self.status is True:
                    self.emit('status-change', False)
                    self.status = False
            self.stopevent.wait(1.0)

    def stop(self):
        self.stopevent.set()
        self.status = False

gobject.type_register(DaemonStatusMonitor)



class ConfigEditor(object):

    def __init__(self):
        self._load_ui()
        self._load_config()
        self.builder.connect_signals(self)
        self.daemon_monitor = None

    def _load_ui(self):
        builder = gtk.Builder()
        builder.add_from_file(
            os.path.join(os.path.dirname(__file__), "uxm-config.glade")
        )
        self.window = builder.get_object('main_window')
        self.save_btn = builder.get_object('save_btn')
        self.save_btn.set_sensitive(False)
        self.close_btn = builder.get_object('close_btn')
        self.main_notebook = builder.get_object('main_notebook')

        # General
        self.filemanager_entry = builder.get_object('filemanager_entry')
        self.filemanager_entry = builder.get_object('filemanager_entry')
        self.filemanager_chooser_btn = builder.get_object('filemanager_chooser_btn')
        self.filemanager_chooser_btn.set_current_folder('/usr/bin')

        self.terminal_entry = builder.get_object('terminal_entry')
        self.terminal_chooser_btn = builder.get_object('terminal_chooser_btn')
        self.terminal_chooser_btn.set_current_folder('/usr/bin')

        self.open_cmd_entry = builder.get_object('open_cmd_entry')
        self.open_cmd_chooser_btn = builder.get_object('open_cmd_chooser_btn')
        self.open_cmd_chooser_btn.set_current_folder('/usr/bin')

        # Icons
        self.icons_show_cb = builder.get_object('icons_show_cb')
        self.icons_size_select = ComboBoxTextDecorator(
            builder.get_object('icons_size_select')
        )
        for s in [16,24,32,48]:
            self.icons_size_select.append_text(s)

        self.use_gtk_theme_cb = builder.get_object('use_gtk_theme_cb')
        self.icons_theme_entry = builder.get_object('icons_theme_entry')
        # ----- defaults
        self.icons_default_app_entry = builder.get_object('icons_default_app_entry')
        self.icons_default_folder_entry = builder.get_object('icons_default_folder_entry')
        self.icons_default_file_entry = builder.get_object('icons_default_file_entry')
        self.icons_default_bookmark_entry = builder.get_object('icons_default_bookmark_entry')
        
        # Menus
        # ----- applications
        self.menu_file_list = ComboBoxTextDecorator(
            builder.get_object('menu_file_list')
        )
        self.menus_apps_show_all_cb = builder.get_object('menus_apps_show_all_cb')
        self.menus_apps_as_submenu_cb = builder.get_object('menus_apps_as_submenu_cb')
        # ----- bookmarks'
        # ----- recent
        self.menus_recent_files_max_items_btn = builder.get_object('menus_recent_files_max_items_btn')
        self.menus_recent_files_max_items_btn.set_adjustment(
            gtk.Adjustment(0, 0, 100, 1)        
        )
        # ----- places
        self.menus_places_start_dir_chooser_btn = builder.get_object('menus_places_start_dir_chooser_btn')
        self.menus_places_show_files_cb = builder.get_object('menus_places_show_files_cb')
        #

        # Daemon
        self.monitor_bookmarks_cb = builder.get_object('monitor_bookmarks_cb')
        self.monitor_recent_cb = builder.get_object('monitor_recent_cb')
        self.formatters_list = ComboBoxTextDecorator(
            builder.get_object('formatters_list')
        )
        self.daemon_status_img =  builder.get_object('daemon_status_img')
        self.daemon_status_lbl =  builder.get_object('daemon_status_lbl')
        self.daemon_start_btn =  builder.get_object('daemon_start_btn')
        self.daemon_stop_btn =  builder.get_object('daemon_stop_btn')
        self.daemon_restart_btn =  builder.get_object('daemon_restart_btn')
        self.daemon_update_btn =  builder.get_object('daemon_update_btn')
        self.daemon_update_all_btn =  builder.get_object('daemon_update_all_btn')
        self.daemon_clear_cache_btn =  builder.get_object('daemon_clear_cache_btn')
        self.daemon_show_btn =  builder.get_object('daemon_show_btn')

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
        self.open_cmd_entry.set_text(
            self.config.get('General', 'open_cmd')            
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
        for f in self._get_menus_list():
            self.menu_file_list.append_text(f)
        self.menus_apps_show_all_cb.set_active(
            self.config.getboolean('Applications', 'show_all')        
        )
        self.menus_apps_as_submenu_cb.set_active(
            self.config.getboolean('Applications', 'as_submenu')        
        )
        # ----- recent
        self.menus_recent_files_max_items_btn.set_value(
            self.config.getint('Recent Files', 'max_items')        
        )
        # ----- places
        self.menus_places_start_dir_chooser_btn.set_current_folder(
            os.path.expanduser(self.config.get('Places', 'start_dir'))
        )
        self.menus_places_show_files_cb.set_active(
            self.config.getboolean('Places', 'show_files')        
        )

        # Daemon
        self.monitor_bookmarks_cb.set_active(
            self.config.getboolean('Daemon', 'monitor_bookmarks')        
        )
        self.monitor_recent_cb.set_active(
            self.config.getboolean('Daemon', 'monitor_recent_files')        
        )
        for f in self._get_formatters_list():
            self.formatters_list.append_text(f)

    def _gather_data(self):
        # General
        monitor_bookmarks = self.monitor_bookmarks_cb.get_active()
        self.config.set('Daemon', 'monitor_bookmarks',
            str(monitor_bookmarks).lower()
        )
        monitor_recent = self.monitor_recent_cb.get_active()
        self.config.set('Daemon', 'monitor_recent_files',
            str(monitor_recent).lower()
        )

        fm = self.filemanager_entry.get_text()
        self.config.set('General', 'filemanager', fm)
        term = self.terminal_entry.get_text()
        self.config.set('General', 'terminal', term)
        open_cmd = self.open_cmd_entry.get_text()
        self.config.set('General', 'open_cmd', open_cmd)

        # Icons
        show_icons = self.icons_show_cb.get_active()
        self.config.set('Icons', 'show', str(show_icons).lower())
        size = self.icons_size_select.get_active_text()
        self.config.set('Icons', 'size', size)
        use_gtk_theme = self.use_gtk_theme_cb.get_active()
        self.config.set('Icons', 'use_gtk_theme', str(use_gtk_theme).lower())
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
        self.config.set('Applications', 'show_all', str(show_all).lower())
        as_submenu = self.menus_apps_as_submenu_cb.get_active()
        self.config.set('Applications', 'as_submenu', str(as_submenu).lower())

        # ----- recent
        max_items = self.menus_recent_files_max_items_btn.get_value()
        self.config.set('Recent Files', 'max_items', max_items)

        # ----- places
        start_dir = self.menus_places_start_dir_chooser_btn.get_filename()
        self.config.set('Places', 'start_dir', start_dir)
        show_files = self.menus_places_show_files_cb.get_active()
        self.config.set('Places', 'show_files', str(show_files).lower())

    def open(self):
        self.window.show_all()

    def main(self):
        gtk.gdk.threads_init()
        gtk.gdk.threads_enter()
        self.open()
        gtk.main()
        gtk.gdk.threads_leave()

    def start_daemon_monitor(self):
        self.daemon_monitor = DaemonStatusMonitor()
        self.daemon_monitor.connect("status-change", self.on_daemon_status_change)
        self.daemon_monitor.start()

    def _get_formatters_list(self):
        formatters = []
        for d in config.PLUGINS_DIRS:
            pathname = os.path.join(d, "*.py")
            for p in glob.iglob(pathname):
                name, _ = os.path.splitext(os.path.basename(p))
                if name not in formatters:
                    formatters.append(name)
        return formatters

    def _get_menus_list(self):
        menus = []
        for d in config.MENU_DIRS:
            pathname = os.path.join(d, '*.menu')
            for p in glob.iglob(pathname):
                name = os.path.basename(p)
                if name not in menus:
                    menus.append(name)
        return menus

    # ---------- Signal handlers ---------- #

    def on_destroy(self, widget, data=None):
        self.daemon_monitor.stop()
        gtk.main_quit()

    def on_changed(self, widget, data=None):
        self.save_btn.set_sensitive(True)

    def on_main_notebook_switch_page(self, notebook, page, page_num, data=None):
        if page_num == 3:
            self.start_daemon_monitor()
        elif self.daemon_monitor:
            self.daemon_monitor.stop()

    def on_use_gtk_theme_cb_toggled(self, widget, data=None):
        self.icons_theme_entry.set_sensitive(
            not widget.get_active()
        )

    def on_terminal_chooser_btn_file_set(self, widget, data=None):
        self.terminal_entry.set_text(widget.get_filename())

    def on_filemanager_chooser_btn_file_set(self, widget, data=None):
        self.filemanager_entry.set_text(widget.get_filename())

    def on_open_cmd_chooser_btn_file_set(self, widget, data=None):
        self.open_cmd_entry.set_text(widget.get_filename())

    def on_save(self, widget, data=None):
        self._gather_data()
        with open(config.USER_CONFIG_FILE, 'w') as fp:
            self.config.write(fp)
            self.save_btn.set_sensitive(False)

    def on_daemon_status_change(self, monitor, status):
        if status:
            self.daemon_status_lbl.set_text("Running")
            self.daemon_status_img.set_from_stock(
                gtk.STOCK_MEDIA_PLAY, gtk.ICON_SIZE_BUTTON
            )
        else:
            self.daemon_status_lbl.set_text("Stopped")
            self.daemon_status_img.set_from_stock(
                gtk.STOCK_MEDIA_STOP, gtk.ICON_SIZE_BUTTON 
            )

    def on_daemon_start_btn_clicked(self, widget, data=None):
        self._gather_data()
        progress.indeterminate(
            "Starting daemon", daemon.start,
            Options(
                formatter = self.formatters_list.get_active_text(),
                menu_file = self.menu_file_list.get_active_text(),
                verbose = False
            )
        )

    def on_daemon_stop_btn_clicked(self, widget, data=None):
        daemon.stop(Options(progress=True))
        
    def on_daemon_restart_btn_clicked(self, widget, data=None):
        self._gather_data()
        progress.indeterminate(
            "Restarting daemon", daemon.start,
            Options(
                formatter = self.formatters_list.get_active_text(),
                menu_file = self.menu_file_list.get_active_text(),
                verbose = False
            )
        )
        
    def on_daemon_update_btn_clicked(self, widget, data=None):
        self._gather_data()
        progress.indeterminate(
            "Updating menus", daemon.update,
            Options(
                formatter = self.formatters_list.get_active_text(),
                menu_file = self.menu_file_list.get_active_text()
            )
        )

    def on_daemon_update_all_btn_clicked(self, widget, data=None):
        self._gather_data()
        progress.indeterminate(
            "Updating all menus", daemon.update_all,
            Options(
                formatter = self.formatters_list.get_active_text(),
                menu_file = self.menu_file_list.get_active_text()
            )
        )

    def on_daemon_clear_cache_btn_clicked(self, widget, data=None):
        self._gather_data()
        progress.indeterminate(
            "Clearing icon cache", daemon.clear_cache,
            Options(
                formatter = self.formatters_list.get_active_text(),
                menu_file = self.menu_file_list.get_active_text()
            )
        )

    def on_daemon_show_btn_clicked(self, widget, data=None):
        self._gather_data()
        uxm.dialogs.menu.clear_cache()
        menu = uxm.dialogs.menu.Menu()
        menu.set_applications_menu_file(self.menu_file_list.get_active_text())
        menu.open()
