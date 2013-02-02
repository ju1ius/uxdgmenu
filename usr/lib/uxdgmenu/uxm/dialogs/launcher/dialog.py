import os
import subprocess
import glib
import gtk
import uxm.bench as bench
from .models import model
from .models.apps_model import AppsModel
from .models.fs_model import FileSystemModel
from .models.pathfinder import PathFinder

(
    MODE_APPS,
    MODE_BROWSE
) = range(2)


class LauncherDialog(object):

    def __init__(self):
        self.pathfinder = PathFinder()
        self.apps_model = AppsModel()
        self.fs_model = FileSystemModel()
        glib.idle_add(self.apps_model.load)
        self.mode = MODE_APPS

        self.keymap = {
            gtk.keysyms.Escape:       self.on_key_press_escape,
            gtk.keysyms.Tab:          self.on_key_press_tab,
            gtk.keysyms.ISO_Left_Tab: self.on_key_press_shift_tab,
            gtk.keysyms.BackSpace:    self.on_key_press_backspace,
            gtk.keysyms.Delete:       self.on_key_press_backspace,
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
        self.treeview = gtk.TreeView(self.apps_model.get_model())
        self.treeview.set_headers_visible(False)
        self.treeview.set_enable_search(False)
        self.treeview.set_hover_selection(True)
        self.treeview.set_can_focus(True)

        col = gtk.TreeViewColumn()
        self.treeview.append_column(col)
        cell = gtk.CellRendererPixbuf()
        col.pack_start(cell, False)
        col.add_attribute(cell, 'pixbuf', model.COLUMN_ICON)

        col = gtk.TreeViewColumn()
        self.treeview.append_column(col)
        cell = gtk.CellRendererText()
        col.pack_start(cell, False)
        col.add_attribute(cell, 'text', model.COLUMN_NAME)

        scrolled.add(self.treeview)
        self.popup.add(scrolled)

        self.SIGNAL_INSERT_TEXT = self.entry.connect('insert-text', self.on_insert_text)
        self.SIGNAL_ENTRY_CHANGED = self.entry.connect_after('changed', self.on_entry_changed)
        #self.entry.connect_after('insert-text', self.on_entry_text_inserted)
        self.entry_window.connect('delete-event', gtk.main_quit)
        self.entry_window.connect('key-press-event', self.on_key_press)

        self.entry_window.show_all()

    def toggle_mode(self, mode):
        self.popup.hide()
        if mode == MODE_APPS:
            pass

    def execute_action(self, data):
        t = data['type']
        if model.TYPE_APP == t:
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

    def suggest(self, mdl, it):
        """Autosuggest of the treeview's selected row"""
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
            filename = mdl.get_value(it, model.COLUMN_NAME)
            pos = text.rfind('/')
            prefix = text[pos+1:]
            suffix = filename[len(prefix):]
            self.entry.insert_text(suffix, -1)
            glib.idle_add(
                lambda: self.entry.select_region(last_index+1, -1),
                priority=glib.PRIORITY_HIGH
            )
        elif self.mode == MODE_APPS:
            name, id = mdl.get(it, model.COLUMN_NAME, model.COLUMN_ID)
            if name.lower().startswith(text.lower()):
                pass
            else:
                item = self.apps_model.data[id]
                name = item['command']
            prefix = text
            suffix = name[text_len:]
            self.entry.insert_text(suffix, -1)
            glib.idle_add(
                lambda: self.entry.select_region(last_index+1, -1),
                priority=glib.PRIORITY_HIGH
            )
        # unblock on_entry_changed handler
        self.entry.handler_unblock(self.SIGNAL_ENTRY_CHANGED)

    def load_directory(self, directory):
        #self.treeview.freeze_child_notify()
        #self.treeview.set_model(None)
        bench.step('Load dir %s' % directory)
        r = self.fs_model.browse(directory)
        bench.endstep('Load dir %s' % directory)
        if r:
            self.treeview.set_model(self.fs_model.get_model())
            self.show_popup()
        #self.treeview.thaw_child_notify()

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

    ##########################################################################
    # ---------- SIGNALS
    ##########################################################################

    def on_insert_text(self, entry, new_text, new_text_len, pos, *args):
        # handle pasted text
        pass 
        if new_text_len > 1:
            first = new_text[0]
            print new_text, entry.get_position(), new_text_len
            #entry.stop_emission('insert-text')
            #if first is '~' or first is '/':
                #self.mode = MODE_BROWSE
                #self.current_range = (pos, pos+new_text_len)


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
        sel = self.treeview.get_selection()
        md, it = sel.get_selected()
        if it is not None:
            sel.unselect_all()
            self.popup.hide()
            self.set_cursor_position(-1)
        else:
            self.quit()

    def on_key_press_enter(self):
        if not self.popup.get_visible():
            return
        sel = self.treeview.get_selection()
        mdl, it = sel.get_selected()
        if it is None:
            it = mdl.get_iter_first()
            if it is None:
                return
        id = mdl.get_value(it, 0)
        if MODE_APPS == self.mode:
            data = self.apps_model.data[id]
            self.execute_action(data)
        elif MODE_BROWSE == self.mode:
            pass

    def on_key_press_tab(self):
        if not self.popup.get_visible():
            return
        sel = self.treeview.get_selection()
        mdl, it = sel.get_selected()
        if it is None:
            it = mdl.get_iter_root()
        t = mdl.get_value(it, model.COLUMN_TYPE)
        print t
        if t == model.TYPE_DIR:
            if self.mode == MODE_BROWSE:
                # complete the path
                self.complete(mdl, it)
                # insert a / at the end, causing the directory to be loaded
                self.entry.insert_text('/', -1)
                # position the cursor at the end
                self.set_cursor_position(-1)
            elif self.mode == MODE_APPS:
                id = mdl.get_value(it, model.COLUMN_ID)
                item = self.apps_model.data[id]
        elif t == model.TYPE_FILE:
            pass
            # complete the path
            # maybe show an action dialog ?
        elif t == model.TYPE_DEV:
            pass
            # complete the path
            # show an action menu (mount/mount and browse)
        elif t == model.TYPE_APP:
            # complete the app command
            id = mdl.get_value(it, model.COLUMN_ID)
            item = self.apps_model.data[id]
            self.entry.set_text(item['command'])
            self.set_cursor_position(-1)

    def on_key_press_shift_tab(self):
        if not self.popup.get_visible():
            return
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

    def on_key_press_backspace(self):
        if self.mode == MODE_BROWSE:
            text = self.entry.get_text()
            if text[-1] != '/':
                return
            last_sep = text.rfind('/', 0, -1)
            if last_sep < 0:
                return
            parent_dir = text[0:last_sep+1]
            self.load_directory(parent_dir)

    def on_key_press_down(self):
        if not self.popup.get_visible():
            return
        sel = self.treeview.get_selection()
        mdl, it = sel.get_selected()
        if it is None:
            sel.select_path((0,))
            self.suggest(mdl, mdl.get_iter_root())
        else:
            next = mdl.iter_next(it)
            if next is None:
                sel.select_path((0,))
                self.treeview.scroll_to_cell((0,))
            else:
                sel.select_iter(next)
                self.treeview.scroll_to_cell(mdl.get_path(next))
            self.suggest(mdl, next)

    def on_key_press_up(self):
        if not self.popup.get_visible():
            return
        sel = self.treeview.get_selection()
        mdl, it = sel.get_selected()
        if it is None:
            sel.select_path((0,))
            self.treeview.scroll_to_cell((0,))
            self.suggest(mdl, mdl.get_iter_root())
        else:
            path = mdl.get_path(it)
            if 0 == path[0]:
                l = mdl.iter_n_children(None)
                it = mdl.iter_nth_child(None, l-1)
                last = mdl.get_path(it)
            else:
                last = (path[0] - 1, )
            sel.select_path(last)
            self.treeview.scroll_to_cell(last)
            self.suggest(mdl, mdl.get_iter(last))

    def on_key_press_left(self):
        pass

    def on_key_press_right(self):
        pass

    def on_entry_changed(self, widget, data=None):
        text = widget.get_text()
        if not text:
            self.popup.hide()
            self.mode = MODE_APPS
            self.treeview.set_model(self.apps_model.get_model())
            return
        cursor_pos = widget.get_position()
        search_range = text[:cursor_pos+1]
        tokens = self.pathfinder.search(search_range)
        if not tokens:
            self.popup.hide()
            self.mode = MODE_APPS
            self.treeview.set_model(self.apps_model.get_model())
            return
        token, token_pos = tokens[-1]
        if len(token) == 1:
            if "~" == token:
                self.mode = MODE_BROWSE
                home = "%s/" % os.path.expanduser(token)
                prefix, suffix = text[:token_pos], text[token_pos + len(token):]
                self.replace_text(prefix + home + suffix)
                return
            if "/" == text:
                self.mode = MODE_BROWSE
                self.load_directory(text)
                num_rows = self.treeview.get_model().iter_n_children(None)
                self.info_label.set_text('%s matche(s)' % num_rows)
                return
            if "!" == text:
                return
            if "$" == text:
                return
        if self.mode == MODE_APPS:
            docs = self.apps_model.find(text)
            if docs:
                self.show_popup()
                self.info_label.set_text('%s matche(s)' % len(docs))
            else:
                self.info_label.set_text('No matches')
                self.popup.hide()
        elif self.mode == MODE_BROWSE:
            if "/" == text[-1]:
                self.load_directory(text)
            else:
                pos = text.rfind('/')
                name = text[pos+1:]
                self.fs_model.filter(name)
        num_rows = self.treeview.get_model().iter_n_children(None)
        if num_rows:
            self.info_label.set_text('%s matche(s)' % num_rows)
        else:
            self.info_label.set_text('No matches')
