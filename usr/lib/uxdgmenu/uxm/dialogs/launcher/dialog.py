import os
#import sys
import subprocess
import collections
import re

import glib
import gtk
import gio

import uxm.bench as bench
from .models import model
from .models.apps_model import AppsModel
from .models.fs_model import FileSystemModel
from .models.pathfinder import PathFinder

(
    MODE_APPS,
    MODE_BROWSE
) = range(2)
DIRECTION_FWD = 1
DIRECTION_BWD = -1
URL_RX = re.compile(r'^\w+://')


class LauncherDialog(object):

    def __init__(self):
#{{{
        gtk.gdk.threads_init()

        # ---------- initialize models
        self.pathfinder = PathFinder()
        self.apps_model = AppsModel()
        self.fs_model = FileSystemModel()
        self.mode = MODE_APPS
        glib.idle_add(self.apps_model.load)

        # ---------- internal properties
        self.current_token = None
        self.current_search = ""
        self.current_search_pos = -1
        # we queue insert/delete events with a small timeout
        # for fast typers, repeated keys, etc...
        self.insert_queue = collections.deque()
        self.delete_queue = collections.deque()

        # ---------- initialize GUI
        self.init_gui()
        # just for testing !!!
        #self.entry.set_text('hello  world')
        #self.set_cursor_position(6)

        # ---------- connect events
        self.SIGNAL_INSERT_TEXT = self.entry.connect('insert-text', self.on_insert_text)
        self.SIGNAL_DELETE_TEXT = self.entry.connect('delete-text', self.on_delete_text)
        #self.SIGNAL_ENTRY_CHANGED = self.entry.connect_after('changed', self.on_entry_changed)
        self.entry_window.connect('delete-event', gtk.main_quit)
        # keyboard events
        self.keymap = {
            gtk.keysyms.Escape:       self.on_key_press_escape,
            gtk.keysyms.Tab:          self.on_key_press_tab,
            gtk.keysyms.ISO_Left_Tab: self.on_key_press_shift_tab,
            gtk.keysyms.Return:       self.on_key_press_enter,
            gtk.keysyms.Down:         self.on_key_press_down,
            gtk.keysyms.Up:           self.on_key_press_up,
            gtk.keysyms.Left:         self.on_key_press_left,
            gtk.keysyms.Right:        self.on_key_press_right,
            gtk.keysyms.h:            self.on_key_press_h
        }
        self.entry_window.connect('key-press-event', self.on_key_press)
        self.treeview.connect('button-release-event', self.on_treeview_mouse_click)
#}}}

    def start(self):
        gtk.gdk.threads_enter()
        gtk.main()
        gtk.gdk.threads_leave()

    def init_gui(self):
#{{{
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

        self.entry_window.show_all()
#}}}

    def token_under_cursor(self, text=None, pos=None):
#{{{
        if text is None:
            text = self.entry.get_text()
        if pos is None:
            pos = self.entry.get_position()
        if not text:
            return None
        tokens = self.pathfinder.search(text)
        num_tokens = len(tokens)
        if num_tokens == 0:
            return None
        # quick checks to speedup the most usual cases
        if num_tokens == 1 or pos <= tokens[0].end:
            return tokens[0]
        if pos > tokens[-1].start:
            return tokens[-1]
        # if cursor is inside a token return it
        # else return the nearest token on the left
        for i, t in enumerate(tokens):
            if t.end >= pos:
                if t.start < pos:
                    return t
                elif i > 0:
                    return tokens[i - 1]
        raise RuntimeError("This should never happen")
#}}}

    def token_before_cursor(self, text=None, pos=None):
#{{{
        if text is None:
            text = self.entry.get_text()
        if pos is None:
            pos = self.entry.get_position()
        if not text:
            return
        tokens = self.pathfinder.search(text[:pos])
        if tokens:
            return tokens[-1]
#}}}

    def set_mode(self, mode):
#{{{
        current_model = self.treeview.get_model()
        if mode == MODE_APPS:
            if current_model is not self.apps_model.get_model():
                self.treeview.set_model(self.apps_model.get_model())
            self.mode = MODE_APPS
        elif mode == MODE_BROWSE:
            if current_model is not self.fs_model.get_model():
                self.treeview.set_model(self.fs_model.get_model())
            self.mode = MODE_BROWSE
#}}}

    def execute_command(self, cmd):
        subprocess.Popen(cmd, shell=True)
        self.quit()

    def handle_url(self, url):
        scheme = url.split(':')[0]
        app_info = gio.app_info_get_default_for_uri_scheme(scheme)
        app_info.launch_uris([url], None)

    def launch_selected(self, mdl, it):
#{{{
        t = mdl.get_value(it, model.COLUMN_TYPE)
        if mdl is self.apps_model.get_model():
            id = mdl.get_value(it, model.COLUMN_ID)
            item = self.apps_model.data[id]
            if t == model.TYPE_APP:
                self.execute_command(item['command'])
            elif t == model.TYPE_DIR:
                self.execute_command(item['command'])
            elif t == model.TYPE_FILE:
                appinfo = gio.app_info_get_default_for_type(item['mimetype'], False)
                if appinfo:
                    appinfo.launch_uris([item['url']], None)
            elif t == model.TYPE_CMD:
                pass
        elif mdl is self.fs_model.get_model():
            name, mimetype = mdl.get(it, model.COLUMN_NAME, model.COLUMN_MIMETYPE)
            path = self.fs_model.last_visited
            filepath = os.path.join(path, name)
            appinfo = gio.app_info_get_default_for_type(mimetype, False)
            gfile = gio.File(filepath)
            if appinfo:
                appinfo.launch([gfile], None)
#}}}

    def insert_text(self, text, pos):
        """Insert text without calling our handlers"""
#{{{
        self.entry.handler_block(self.SIGNAL_INSERT_TEXT)
        self.entry.insert_text(text, pos)
        self.entry.handler_unblock(self.SIGNAL_INSERT_TEXT)
#}}}

    def set_entry_text(self, text):
        """Sets the entry's text without calling our handlers"""
#{{{
        #self.entry.handler_block(self.SIGNAL_ENTRY_CHANGED)
        self.entry.handler_block(self.SIGNAL_INSERT_TEXT)
        self.entry.handler_block(self.SIGNAL_DELETE_TEXT)

        self.entry.set_text(text)

        #self.entry.handler_unblock(self.SIGNAL_ENTRY_CHANGED)
        self.entry.handler_unblock(self.SIGNAL_INSERT_TEXT)
        self.entry.handler_unblock(self.SIGNAL_DELETE_TEXT)
#}}}

    def set_cursor_position(self, position):
        """Sets the cursor position by calling glib.idle_add
        To be used when we insert/remove text without blocking handlers
        """
        glib.idle_add(
            lambda: self.entry.set_position(position),
            priority=glib.PRIORITY_HIGH
        )

    def replace_text(self, start, end, newtext):
        """Replace text from start to end by newtext, without calling our handlers"""
#{{{
        oldtext = self.entry.get_text()
        prefix, suffix = oldtext[:start], oldtext[end:]
        before_cursor = prefix + newtext
        self.set_entry_text(before_cursor + suffix)
        self.entry.set_position(len(before_cursor))
#}}}

    def suggest(self, mdl, it):
        """Autosuggest of the treeview's selected row"""
#{{{
        #print "SUGGEST"
        # prevent our on_entry_changed handler to be called
        #self.entry.handler_block(self.SIGNAL_ENTRY_CHANGED)
        self.entry.handler_block(self.SIGNAL_DELETE_TEXT)

        # first clear previous selection
        selection = self.entry.get_selection_bounds()
        if selection:
            self.entry.delete_selection()

        # get the text
        text = self.entry.get_text()
        pos = self.entry.get_position()
        search = self.current_search
        search_pos = self.current_search_pos
        search_len = len(search)
        endpos = search_pos + search_len

        if pos != search_pos and not selection:
            # user has moved the cursor between row selection
            # let's try to remember the previously inserted suggestion
            tokens = self.pathfinder.search(text[endpos:])
            if tokens:
                token = tokens[0]
                if token.start == 0:
                    self.entry.delete_text(endpos, endpos + token.length)

        if self.mode == MODE_BROWSE:
            filename = mdl.get_value(it, model.COLUMN_NAME)
            suffix = filename[search_len:]
            self.insert_text(suffix, endpos)
            self.entry.select_region(endpos, endpos + len(suffix))
        elif self.mode == MODE_APPS:
            id, type, name = mdl.get(it, model.COLUMN_ID, model.COLUMN_TYPE, model.COLUMN_NAME)
            if type == model.TYPE_APP:
                pass
            else:
                suffix = name[search_len:]
                #print search, suffix, search_pos, repr(self.current_token), endpos
                self.insert_text(suffix, search_pos)
                self.entry.select_region(search_pos, search_pos + len(suffix))

        # unblock on_entry_changed handler
        self.entry.handler_unblock(self.SIGNAL_DELETE_TEXT)
        #self.entry.handler_unblock(self.SIGNAL_ENTRY_CHANGED)
#}}}

    def load_directory(self, directory):
#{{{
        bench.step('Load dir %s' % directory)
        r = self.fs_model.browse(directory)
        bench.endstep('Load dir %s' % directory)
        if r:
            self.treeview.set_model(self.fs_model.get_model())
            self.show_popup()
#}}}

    def quit(self):
        self.apps_model.kill_threads()
        gtk.main_quit()
        #sys.exit(0)

    def show_popup(self):
        self.position_popup()
        self.popup.show_all()

    def position_popup(self):
#{{{
        ox, oy = self.entry.window.get_origin()
        w, h = self.entry.window.get_size()
        self.popup.move(ox, oy + h)
        self.popup.set_size_request(w, 256)
#}}}

    def show_action_menu(self):
#{{{
        sel = self.treeview.get_selection()
        mdl, it = sel.get_selected()
        if it is None:
            # no selection: execute the command in text entry
            return
        # selection: execute chosen command
        id, type = mdl.get(it, model.COLUMN_ID, model.COLUMN_TYPE)
        if type == model.TYPE_APP:
            return
        if MODE_APPS == self.mode:
            menu = self.apps_model.get_action_menu(id)
        elif MODE_BROWSE == self.mode:
            menu = self.fs_model.get_action_menu(it)
        menu.foreach(lambda item: item.connect('activate', self.on_menuitem_activate))
        menu.show_all()
        menu.popup(None, None, self.position_action_menu, 0, 0, mdl.get_path(it))
#}}}

    def position_action_menu(self, menu, path):
        cell_rect = self.treeview.get_cell_area(path, self.treeview.get_column(0))
        ox, oy = self.popup.window.get_origin()
        w, h = self.popup.window.get_size()
        return (ox + w, oy + cell_rect.y, True)

    ##########################################################################
    # ---------- SIGNALS
    ##########################################################################

    def on_menuitem_activate(self, menuitem, *args):
        if hasattr(menuitem, 'appinfo'):
            menuitem.appinfo.launch([menuitem.file])
        else:
            self.execute_command(menuitem.command)

    #FIXME: There is one drawback to setting timeouts on these events:
    # if the user quickly interleaves them or moves the cursor in between
    # two quick insertions/deletions, then the text and positions
    # reported by the original event handler become invalid...
    # => Maybe use a single queue, pass it to a single callback
    # that determines what action to execute,
    # along with the correct text and positions ?

    def on_insert_text(self, *args):
        self.insert_queue.append(args)
        glib.timeout_add(250, self.on_insert_text_callback)

    def on_delete_text(self, entry, start, end, *args):
        text = self.entry.get_text()
        self.delete_queue.append((entry, start, end, text[start]))
        glib.timeout_add(250, self.on_delete_text_callback)

    def on_insert_text_callback(self, *args):
#{{{
        # args passed to the queue are those of on_insert_text
        # entry, new_text, new_text_len, pos, *user_params
        if len(self.insert_queue) == 0:
            # we return here because the function is
            # still called even if there are no events in the queue
            return
        entry = self.insert_queue[0][0]
        new_text, new_text_len = "", 0
        for event in self.insert_queue:
            new_text += event[1]
            new_text_len += event[2]
        self.insert_queue.clear()

        print "INSERT"
        text = entry.get_text()
        pos = entry.get_position()
        token = self.token_before_cursor(text, pos)
        if not token:
            self.popup.hide()
            self.set_mode(MODE_APPS)
            return
        # Check what mode we're in
        if pos > token.end:
            # if cursor is in between tokens,
            # it means we inserted some sort of unescaped whitespace
            return
        #print repr(token)
        # If the current token looks like a path...
        if "~" == token[0]:
            print "I see a path:", token
            self.mode = MODE_BROWSE
            path = os.path.expanduser(token.value)
            if len(token) == 1:
                path += '/'
            #entry.stop_emission('insert-text')
            #self.insert_text(path, token.start)
            #self.set_cursor_position(token.start + len(path))
            self.replace_text(token.start, token.end, path)
            token.value = path
        elif token.absolute:
            print "I see a path:", token
            self.mode = MODE_BROWSE
        #elif token.value.find('/') != -1:
            #path = os.path.expanduser('~/%s' % token.value)
            #if os.path.exists(path):
                #self.mode = MODE_BROWSE
                #token.value = path
        else:
            print "I see a search:", token
            self.mode = MODE_APPS
        # setup variables for suggest & complete
        self.current_token = token
        self.current_search = token.value
        self.current_search_pos = token.end

        if self.mode == MODE_APPS:
            docs = self.apps_model.find(token.value)
            if docs:
                self.treeview.set_model(self.apps_model.get_model())
                self.show_popup()
                self.info_label.set_text('%s matche(s)' % len(docs))
            else:
                self.info_label.set_text('No matches')
                self.popup.hide()
        elif self.mode == MODE_BROWSE:
            if "/" == token[-1]:
                self.load_directory(token.value)
                self.current_search = ""
                self.current_search_pos = token.end
            else:
                pos = token.value.rfind('/')
                name = token[pos + 1:]
                self.current_search = name
                self.current_search_pos = token.start + pos + 1
                self.fs_model.filter(name)

        mdl = self.treeview.get_model()
        num_rows = mdl.iter_n_children(None)
        if num_rows == 0:
            self.info_label.set_text('No matches')
        elif num_rows == 1:
            self.info_label.set_text('Unique match')
            glib.idle_add(self.suggest, mdl, mdl.get_iter_root())
        else:
            self.info_label.set_text('%s matches' % num_rows)
#}}}

    def on_delete_text_callback(self, *args):
#{{{
        # args passed to the queue are those of on_delete_text
        # entry, start, end, + last_deleted_char
        if len(self.delete_queue) == 0:
            # we return here because the function is
            # still called even if there are no events in the queue
            return
        unzipped = zip(*self.delete_queue)
        entry = unzipped[0][0]
        start, end = min(unzipped[1]), max(unzipped[2])
        last_deleted_char = unzipped[3][-1]
        self.delete_queue.clear()

        text = entry.get_text()
        pos = entry.get_position()
        print "DELETE FROM %s to %s, %s" % (start, end, last_deleted_char)
        #print text[start - 1]
        token = self.token_before_cursor(text, pos)
        if not token:
            self.popup.hide()
            self.set_mode(MODE_APPS)
            return
        if pos > token.end:
            return

        if token.absolute:
            print "I see a path:", token
            self.mode == MODE_BROWSE
        else:
            print "I see a search:", token
            self.mode == MODE_APPS

        self.current_token = token
        self.current_search = token.value
        self.current_search_pos = token.end

        if self.mode == MODE_BROWSE:
            pos = token.rfind('/')
            if pos == 0:
                parent_dir = '/'
                search = token[1:] if len(token) > 1 else ''
            else:
                parent_dir, search = token[:pos], token[pos + 1:]
            self.current_search = search
            self.current_search_pos = token.start + pos + 1
            self.load_directory(parent_dir)
            self.fs_model.filter(search)
        elif self.mode == MODE_APPS:
            docs = self.apps_model.find(token.value)
            if docs:
                self.treeview.set_model(self.apps_model.get_model())
                self.show_popup()
                self.info_label.set_text('%s matche(s)' % len(docs))
            else:
                self.info_label.set_text('No matches')
                self.popup.hide()
#}}}

    def on_key_press(self, widget, event, data=None):
        key = event.keyval
        #print "Result: %s" % self.token_under_cursor()
        if key in self.keymap:
            self.keymap[key](event)
        else:
            for keysym in dir(gtk.keysyms):
                keyval = getattr(gtk.keysyms, keysym)
                if keyval == key:
                    print keysym, key
                    pass

    def on_key_press_escape(self, event):
        sel = self.treeview.get_selection()
        #md, it = sel.get_selected()
        if self.popup.get_visible():  # or it is not None:
            sel.unselect_all()
            self.popup.hide()
            #self.set_cursor_position(-1)
        else:
            self.quit()

    def on_key_press_enter(self, event):
#{{{
        text = self.entry.get_text()
        if not text:
            return
        if event.state & gtk.gdk.CONTROL_MASK:
            # launch in terminal
            self.execute_command('x-terminal-emulator -e "%s"' % text)
            return
        tokens = self.pathfinder.search(text)
        if len(tokens) == 1:
            if URL_RX.match(tokens[0].value):
                self.handle_url(tokens[0].value)
                return
        sel = self.treeview.get_selection()
        mdl, it = sel.get_selected()
        if it is None:
            self.execute_command(text)
            return
        self.launch_selected(mdl, it)
#}}}

    def on_key_press_tab(self, event):
#{{{
        if not self.popup.get_visible():
            return
        self.entry_window.stop_emission('key-press-event')

        sel = self.treeview.get_selection()
        mdl, it = sel.get_selected()
        if it is None:
            it = mdl.get_iter_root()
            self.suggest(mdl, it)
        #FIXME: do we really need the selection bounds ?
        bounds = self.entry.get_selection_bounds()
        t = mdl.get_value(it, model.COLUMN_TYPE)
        if mdl == self.fs_model.get_model():
            if bounds:
                if t == model.TYPE_DIR:
                    # insert a / at the end, causing the directory to be loaded
                    self.entry.insert_text('/', bounds[1])
                    self.set_cursor_position(bounds[1] + 1)
                else:
                    # position cursor at end and close popup
                    self.set_cursor_position(bounds[1])
                    self.popup.hide()
        elif mdl == self.apps_model.get_model():
            if t == model.TYPE_DIR or t == model.TYPE_FILE:
                # complete the path
                # could also be an url so handle this case too ?
                id = mdl.get_value(it, model.COLUMN_ID)
                item = self.apps_model.data[id]
                url = item['url']
                if url.startswith('file://'):
                    url = url.replace('file://', '')
                self.entry.delete_selection()
                txt = self.entry.get_text()
                token = self.current_token
                prefix, suffix = txt[:token.start], txt[:token.end]
                self.set_entry_text(prefix + url + txt[token.end:])
                endpos = len(prefix) + len(url)
                self.set_cursor_position(endpos)
                if t == model.TYPE_DIR:
                    # insert a / at the end, causing the directory to be loaded
                    self.entry.insert_text('/', endpos)
                    self.set_cursor_position(endpos + 1)
            elif t == model.TYPE_DEV:
                pass
            elif t == model.TYPE_APP:
                # complete the app command
                id = mdl.get_value(it, model.COLUMN_ID)
                item = self.apps_model.data[id]
                txt = self.entry.get_text()
                token = self.current_token
                prefix, suffix = txt[:token.start], txt[:token.end]
                self.set_entry_text(prefix + item['command'] + txt[token.end:])
                self.set_cursor_position(len(prefix) + len(item['command']))
            elif t == model.TYPE_CMD:
                if bounds:
                    self.set_cursor_position(bounds[1])
#}}}

    def on_key_press_shift_tab(self, event):
#{{{
        if not self.popup.get_visible():
            return
        text = self.entry.get_text()
        if not text:
            return
        pos = self.entry.get_position()
        search_range = text[:pos]
        if not search_range:
            return
        tokens = self.pathfinder.search(search_range)
        if not tokens:
            return
        token = tokens[-1]
        if token.absolute:
            self.mode = MODE_BROWSE
            last_sep = token.rfind('/')
            if last_sep < 1:
                # no parent dir or at root
                return
            elif last_sep == token.length - 1:
                # path ends with a slash, find previous one
                last_sep = token.rfind('/', 0, -1)
            # load parent dir
            delete_pos = token.start + last_sep + 1
            self.entry.delete_text(delete_pos, token.end)
            self.set_cursor_position(delete_pos)
            #parent_dir = token[:last_sep]
            #self.entry.delete_text(token.start, token.end)
            #self.entry.insert_text("%s/" % parent_dir, token.start)
            #self.set_cursor_position(token.start + len(parent_dir) + 1)
#}}}

    def on_key_press_down(self, event):
#{{{
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
                next = mdl.get_iter_root()
            sel.select_iter(next)
            self.treeview.scroll_to_cell(mdl.get_path(next))
            self.suggest(mdl, next)
#}}}

    def on_key_press_up(self, event):
#{{{
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
                it = mdl.iter_nth_child(None, l - 1)
                last = mdl.get_path(it)
            else:
                last = (path[0] - 1,)
            sel.select_path(last)
            self.treeview.scroll_to_cell(last)
            self.suggest(mdl, mdl.get_iter(last))
#}}}

    def on_key_press_left(self, event):
        #TODO: close action menu if visible
        if self.popup.get_visible():
            self.popup.hide()
            return

    def on_key_press_right(self, event):
        if not self.popup.get_visible():
            return
        self.entry_window.stop_emission('key-press-event')
        self.show_action_menu()

    def on_key_press_h(self, event):
        if event.state & gtk.gdk.CONTROL_MASK:
            #TODO: toggle show hidden files
            return

    def on_treeview_mouse_click(self, treeview, event, *args):
        if event.button == 1:  # left click
            #TODO: complete
            pass
        elif event.button == 3:  # right click
            self.show_action_menu()
