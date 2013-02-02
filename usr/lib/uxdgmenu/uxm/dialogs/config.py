import os, glob, threading

import pygtk
pygtk.require('2.0')
import gtk, gobject

import uxm.config as config
import uxm.utils as utils
import uxm.dialogs.progress as progress
import uxm.daemon as daemon
import uxm.dialogs.menu
from uxm.dialogs.helpers import ComboBoxTextDecorator


class Options(object):
    """Mock OptionsParser options"""
    def __init__(self, **kwargs):
        # Defaults
        self.with_applications = None
        self.with_bookmarks = None
        self.with_recent_files = None
        self.with_devices = None
        # Overrides
        for prop, val in kwargs.iteritems():
            self.__dict__[prop] = val


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
            pids = utils.proc.pgrep('uxdgmenud', exact=True, user=os.environ['USER'])
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
            os.path.join(os.path.dirname(__file__), "config.ui")
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
        for d in ['application','folder','file','bookmark','internal_drive',
                    'optical_drive','removable_drive','mount','unmount']:
            obj = 'icons_default_%s_entry' % d
            setattr(self, obj, builder.get_object(obj))
        
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
        for a in ['applications','bookmarks','recent_files','devices']:
            attr = "monitor_%s_cb" % a
            setattr(self, attr, builder.get_object(attr))
        self.formatters_list = ComboBoxTextDecorator(
            builder.get_object('formatters_list')
        )
        self.daemon_status_img =  builder.get_object('daemon_status_img')
        self.daemon_status_lbl =  builder.get_object('daemon_status_lbl')
        for a in ['start','stop','restart','update',
                    'update_all','clear_cache','show']:
            attr = "daemon_%s_btn" % a
            setattr(self, attr, builder.get_object(attr))

        self.builder = builder

    def _load_config(self):
        self.prefs = config.preferences()
        # General
        for p in ['filemanager','terminal','open_cmd']:
            getattr(self, "%s_entry" % p).set_text(
                self.prefs.get('General', p)
            )
        # Icons
        self.icons_show_cb.set_active(
            self.prefs.getboolean('Icons', 'show')        
        )
        # ----- get icon size
        s = self.prefs.getint('Icons', 'size')
        if s < 16: s = 16
        # ---------- round to the nearest multiple of 8
        icon_size = utils.fmt.round_base(s, 8)
        # ---------- compute index
        self.icons_size_select.set_active((icon_size / 8) - 2)
        # ----- theme
        self.use_gtk_theme_cb.set_active(
            self.prefs.getboolean('Icons', 'use_gtk_theme')        
        )
        self.icons_theme_entry.set_text(
            self.prefs.get('Icons', 'theme')        
        )
        self.icons_theme_entry.set_sensitive(
            not self.use_gtk_theme_cb.get_active()
        )
        # ----- defaults
        for d in ['application','folder','file','bookmark','internal_drive',
                    'optical_drive','removable_drive','mount','unmount']:
            attr = getattr(self, 'icons_default_%s_entry' % d)
            attr.set_text(self.prefs.get('Icons', d))

        # Menus
        # ----- apps
        for f in self._get_menus_list():
            self.menu_file_list.append_text(f)
        self.menu_file_list.set_active_text(
            self.prefs.get('Applications', 'menu_file')        
        )
        self.menus_apps_show_all_cb.set_active(
            self.prefs.getboolean('Applications', 'show_all')        
        )
        self.menus_apps_as_submenu_cb.set_active(
            self.prefs.getboolean('Applications', 'as_submenu')        
        )
        # ----- recent
        self.menus_recent_files_max_items_btn.set_value(
            self.prefs.getint('Recent Files', 'max_items')        
        )
        # ----- places
        self.menus_places_start_dir_chooser_btn.set_current_folder(
            os.path.expanduser(self.prefs.get('Places', 'start_dir'))
        )
        self.menus_places_show_files_cb.set_active(
            self.prefs.getboolean('Places', 'show_files')        
        )

        # Daemon
        for a in ['applications','bookmarks','recent_files','devices']:
            getattr(self, 'monitor_%s_cb' % a).set_active(
                self.prefs.getboolean('Daemon', 'monitor_%s' % a)            
            )
        for f in self._get_formatters_list():
            self.formatters_list.append_text(f)

    def _gather_data(self):
        # General
        for p in ['filemanager','terminal','open_cmd']:
            self.prefs.set(
                'General', p,
                getattr(self, "%s_entry" % p).get_text()
            )
        # Icons
        show_icons = self.icons_show_cb.get_active()
        self.prefs.set('Icons', 'show', str(show_icons).lower())
        size = self.icons_size_select.get_active_text()
        self.prefs.set('Icons', 'size', size)
        use_gtk_theme = self.use_gtk_theme_cb.get_active()
        self.prefs.set('Icons', 'use_gtk_theme', str(use_gtk_theme).lower())
        theme = self.icons_theme_entry.get_text()
        self.prefs.set('Icons', 'theme', theme)
        # ----- defaults
        for d in ['application','folder','file','bookmark','internal_drive',
                    'optical_drive','removable_drive','mount','unmount']:
            attr = getattr(self, 'icons_default_%s_entry' % d)
            self.prefs.set('Icons', d, attr.get_text())
            attr.set_text(self.prefs.get('Icons', d))

        # Menus
        # ----- apps
        menu_file = self.menu_file_list.get_active_text()
        self.prefs.set('Applications', 'menu_file', menu_file)
        show_all = self.menus_apps_show_all_cb.get_active()
        self.prefs.set('Applications', 'show_all', str(show_all).lower())
        as_submenu = self.menus_apps_as_submenu_cb.get_active()
        self.prefs.set('Applications', 'as_submenu', str(as_submenu).lower())
        # ----- recent
        max_items = self.menus_recent_files_max_items_btn.get_value()
        self.prefs.set('Recent Files', 'max_items', int(max_items))
        # ----- places
        start_dir = self.menus_places_start_dir_chooser_btn.get_filename()
        self.prefs.set('Places', 'start_dir', start_dir)
        show_files = self.menus_places_show_files_cb.get_active()
        self.prefs.set('Places', 'show_files', str(show_files).lower())

        # Daemon
        for a in ['applications','bookmarks','recent_files','devices']:
            val = getattr(self, "monitor_%s_cb" % a).get_active()
            self.prefs.set('Daemon', 'monitor_%s' % a, str(val).lower())

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
        if self.daemon_monitor:
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
            self.prefs.write(fp)
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
            ),
            parent = self.window
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
            ),
            parent = self.window
        )
        
    def on_daemon_update_btn_clicked(self, widget, data=None):
        self._gather_data()
        progress.indeterminate(
            "Updating menus", daemon.update,
            Options(
                formatter = self.formatters_list.get_active_text(),
                menu_file = self.menu_file_list.get_active_text()
            ),
            parent = self.window
        )

    def on_daemon_update_all_btn_clicked(self, widget, data=None):
        self._gather_data()
        progress.indeterminate(
            "Updating all menus", daemon.update_all,
            Options(
                formatter = self.formatters_list.get_active_text(),
                menu_file = self.menu_file_list.get_active_text()
            ),
            parent = self.window
        )

    def on_daemon_clear_cache_btn_clicked(self, widget, data=None):
        self._gather_data()
        progress.indeterminate(
            "Clearing icon cache", daemon.clear_cache,
            Options(
                formatter = self.formatters_list.get_active_text(),
                menu_file = self.menu_file_list.get_active_text()
            ),
            parent = self.window
        )

    def on_daemon_show_btn_clicked(self, widget, data=None):
        self._gather_data()
        uxm.dialogs.menu.clear_cache()
        menu = uxm.dialogs.menu.Menu()
        menu.set_applications_menu_file(self.menu_file_list.get_active_text())
        menu.open()
