import os, sys, subprocess
import glib, gtk
import uxm.bench as bench
from . import model, pathfinder
from .constants import *

class LauncherDialog(object):

    def __init__(self):
        self.model = model.Model()
        self.pathfinder = pathfinder.PathFinder()
        #bench.step('Load apps')
        self.model.load_apps()
        #bench.endstep('Load apps')
        self.mode = MODE_APPS
        # Flag to avoid triggering Entry::change signal after automatic text insertion
        self.text_inserted = False

        self.keymap = {
            gtk.keysyms.Escape:       self.on_key_press_escape,
            gtk.keysyms.Tab:          self.on_key_press_tab,
            gtk.keysyms.ISO_Left_Tab: self.on_key_press_shift_tab,
            gtk.keysyms.Return:       self.on_key_press_enter,
            gtk.keysyms.Down:         self.on_key_press_down,
            gtk.keysyms.Up:           self.on_key_press_up,
            gtk.keysyms.Left:         self.on_key_press_left,
            gtk.keysyms.Right:        self.on_key_press_right
        }

        # Text box window
        self.entry_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.entry_window.set_size_request(500, 120)
        self.entry_window.set_position(gtk.WIN_POS_CENTER_ALWAYS)

        vbox = gtk.VBox()
        vbox.set_homogeneous(False)
        vbox.set_spacing(0)
        self.info_label = gtk.Label()
        vbox.pack_start(self.info_label, False, False, 4)
        self.entry = gtk.Entry()
        vbox.pack_start(self.entry, False, False, 4)

        self.entry_window.add(vbox)

        # Search results popup
        self.popup = gtk.Window(gtk.WINDOW_POPUP)
        self.popup.set_transient_for(self.entry_window)
        self.popup.set_size_request(500, 200)
        self.popup.set_position(gtk.WIN_POS_CENTER_ON_PARENT)

        scrolled = gtk.ScrolledWindow()
        scrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.treeview = gtk.TreeView(self.model.store)
        self.treeview.set_headers_visible(False)
        self.treeview.set_enable_search(False)
        self.treeview.set_hover_selection(True)
        self.treeview.set_can_focus(True)

        col = gtk.TreeViewColumn()
        self.treeview.append_column(col)
        cell = gtk.CellRendererPixbuf()
        col.pack_start(cell, False)
        col.add_attribute(cell, 'pixbuf', COLUMN_ICON)

        col = gtk.TreeViewColumn()
        self.treeview.append_column(col)
        cell = gtk.CellRendererText()
        col.pack_start(cell, False)
        col.add_attribute(cell, 'text', COLUMN_NAME)

        scrolled.add(self.treeview)
        self.popup.add(scrolled)

        self.SIGNAL_ENTRY_CHANGED = self.entry.connect_after('changed', self.on_entry_changed)
        #self.entry.connect_after('insert-text', self.on_entry_text_inserted)
        self.entry_window.connect('delete-event', gtk.main_quit)
        self.entry_window.connect('key-press-event', self.on_key_press)

        self.entry_window.show_all()

    def execute_action(self, data):
        t = data['type']
        if TYPE_APP == t:
            self.execute_command(data['command'])

    def execute_command(self, cmd):
        subprocess.Popen(cmd, shell=True)
        self.quit()

    def set_cursor_position(self, position):
        glib.idle_add(
            lambda: self.entry.set_position(position),
            priority=glib.PRIORITY_HIGH
        )

    def replace_text(self, text):
        self.entry.set_text(text)
        self.set_cursor_position(-1)

    def complete(self, model, it):
        """Autocompletion of the treeview's selected row"""
        # prevent our on_entry_changed handler to be called
        self.entry.handler_block(self.SIGNAL_ENTRY_CHANGED)

        # first clear previous selection
        selection = self.entry.get_selection_bounds()
        if selection:
            self.entry.delete_selection()
        # get the text
        text = self.entry.get_text()
        text_len = len(text)
        last_index = text_len - 1

        if self.mode == MODE_BROWSE:
            filename = model.get_value(it, COLUMN_NAME)
            pos = text.rfind('/')
            prefix = text[pos+1:]
            suffix = filename[len(prefix):]
            self.entry.insert_text(suffix, -1)
            glib.idle_add(
                lambda: self.entry.select_region(last_index+1, -1),
                priority=glib.PRIORITY_HIGH
            )
        # unblock on_entry_changed handler
        self.entry.handler_unblock(self.SIGNAL_ENTRY_CHANGED)

    def load_directory(self, directory):
        bench.step('Load dir %s' % directory)
        r = self.pathfinder.browse(directory)
        bench.endstep('Load dir %s' % directory)
        if r:
            self.treeview.set_model(self.pathfinder.model_filter)
            self.show_popup()

    def quit(self):
        gtk.main_quit()
        #sys.exit(0)

    def show_popup(self):
        self.position_popup()
        self.popup.show_all()

    def position_popup(self):
        ox, oy = self.entry.window.get_origin()
        w, h = self.entry.window.get_size()
        self.popup.move(ox, oy + h)
        self.popup.set_size_request(w, 256)

    # SIGNALS

    def on_key_press(self, widget, event, data=None):
        key = event.keyval
        if key in self.keymap:
            self.keymap[key]()
        else:
            for keysym in dir(gtk.keysyms):
                keyval = getattr(gtk.keysyms, keysym)
                if keyval == key:
                    print keysym, key

    def on_key_press_escape(self):
        self.quit()

    def on_key_press_enter(self):
        sel = self.treeview.get_selection()
        model, it = sel.get_selected()
        if it is None:
            it = model.get_iter_first()
            if it is None:
                return
        id = model.get_value(it, 0)
        if MODE_APPS == self.mode:
            data = self.model.data[id]
            self.execute_action(data)
        elif MODE_BROWSE == self.mode:
            pass

    def on_key_press_tab(self):
        sel = self.treeview.get_selection()
        model, it = sel.get_selected()
        if it is None:
            # no selection, complete if we have only one result
            return
        t = model.get_value(it, COLUMN_TYPE)
        if t == TYPE_DIR:
            # complete the path
            self.complete(model, it)
            # insert a / at the end, causing the directory to be loaded
            self.entry.insert_text('/', -1)
            # position the cursor at the end
            self.set_cursor_position(-1)
        elif t == TYPE_FILE:
            pass
            # complete the path
            # maybe show an action dialog ?
        elif t == TYPE_DEV:
            pass
            # complete the path
            # show an action menu (mount/mount and browse)
        elif t == TYPE_APP:
            pass
            # complete the app name

    def on_key_press_shift_tab(self):
        if self.mode == MODE_BROWSE:
            text = self.entry.get_text()
            last_sep = text.rfind('/')
            if last_sep < 1:
                # no parent dir or at root
                return
            elif last_sep == len(text) - 1:
                # path ends with a slash, find previous one
                last_sep = text.rfind('/', 0, -1)
            parent_dir = text[0:last_sep]
            # load parent dir
            self.entry.set_text("%s/" % parent_dir)
            self.set_cursor_position(-1)

    def on_key_press_down(self):
        sel = self.treeview.get_selection()
        model, it = sel.get_selected()
        if it is None:
            sel.select_path((0,))
            self.complete(model, model.get_iter_root())
        else:
            next = model.iter_next(it)
            if next is None:
                sel.select_path((0,))
                self.treeview.scroll_to_cell((0,))
            else:
                sel.select_iter(next)
                self.treeview.scroll_to_cell(model.get_path(next))
            self.complete(model, next)

    def on_key_press_up(self):
        sel = self.treeview.get_selection()
        model, it = sel.get_selected()
        if it is None:
            sel.select_path((0,))
            self.treeview.scroll_to_cell((0,))
            self.complete(model, model.get_iter_root())
        else:
            path = model.get_path(it)
            if 0 == path[0]:
                l = model.iter_n_children(None)
                it = model.iter_nth_child(None, l-1)
                last = model.get_path(it)
            else:
                last = (path[0] - 1, )
            sel.select_path(last)
            self.treeview.scroll_to_cell(last)
            self.complete(model, model.get_iter(last))

    def on_key_press_left(self):
        pass
    def on_key_press_right(self):
        pass

    def on_entry_changed(self, widget, data=None):
        text = widget.get_text()
        print text
        if not text:
            return
        elif len(text) == 1:
            if "~" == text:
                self.mode = MODE_BROWSE
                home = "%s/" % os.path.expanduser(text)
                self.replace_text(home)
                return
            elif "/" == text:
                self.mode = MODE_BROWSE
                glib.idle_add(self.load_directory, text)
                return
            else:
                self.mode = MODE_BROWSE
        elif self.mode == MODE_APPS:
            docs = self.model.find(text)
            if docs:
                self.show_popup()
                self.info_label.set_text('%s matche(s)' % len(docs))
            else:
                self.info_label.set_text('No matches')
                self.popup.hide()
        elif self.mode == MODE_BROWSE:
            if "/" == text[-1]:
                glib.idle_add(self.load_directory, text)
            else:
                pos = text.rfind('/')
                name = text[pos+1:]
                self.pathfinder.filter(name)
            return
