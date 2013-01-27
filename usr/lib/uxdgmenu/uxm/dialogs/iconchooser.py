import os, re
import glib, gobject, gtk
from xdg.BaseDirectory import xdg_data_dirs

import uxm.config as config
_ = config.translate

import uxm.dialogs.helpers as helpers

__DIR__ = os.path.dirname(os.path.abspath(__file__))
UI_FILE = os.path.join(__DIR__, 'iconchooser.ui')


ICON_EXT_RX = re.compile(r'.*\.(png|svg|xpm)$', re.I)

class ContextSelect(helpers.WidgetDecorator):

    def __init__(self, widget):
        super(ContextSelect, self).__init__(widget)
        self.model = gtk.ListStore(str, str)
        cell = gtk.CellRendererText()
        self.widget.pack_start(cell, True)
        self.widget.add_attribute(cell, 'text', 1)
        self.widget.set_model(self.model)
        self.widget.set_row_separator_func(self.row_separator_callback)

    def set_theme(self, theme):
        self.model.append(('all', 'All'))
        self.model.append(('', ''))
        contexts = theme.list_contexts()
        for ctx in sorted(contexts):
            self.model.append((ctx, _(ctx)))
        self.model.append(('', ''))
        self.model.append(('pixmaps', 'Pixmaps'))

    def get_active_context(self):
        i = self.widget.get_active()
        row = self.model[i]
        return row[0]

    def set_active_context(self, ctx):
        for i, row in enumerate(self.model):
            if row[0] == ctx:
                self.widget.set_active(i)

    def row_separator_callback(self, model, it, data=None):
        context = model.get_value(it, 0)
        if '' == context:
            return True


class IconChooser(helpers.BuildableWidgetDecorator):

    COLUMN_NAME = 0
    COLUMN_PATH = 1
    COLUMN_PIXBUF = 2

    def __init__(self):
        # UI setup
        super(IconChooser, self).__init__(UI_FILE, 'iconchooser_dialog')
        self.add_ui_widgets(
            'context_lbl', 'search_lbl',
            'context_select', 'search_entry',
            'iconview', 'size_select', 'apply_btn', 'cancel_btn'
        )

        self.model = gtk.ListStore(str, str, gtk.gdk.Pixbuf)
        self.model_filter = self.model.filter_new()
        self.model_filter.set_visible_func(self.search_callback)

        self.iconview.set_model(self.model_filter)
        self.iconview.set_text_column(self.COLUMN_NAME)
        self.iconview.set_pixbuf_column(self.COLUMN_PIXBUF)

        self.size_select = helpers.ComboBoxTextDecorator(self.size_select)

        for size in (16, 24, 32, 48, 64, 128):
            self.size_select.append_text(size)
        # Set default icon size
        self.size_select.set_active(2)
        self.set_icon_size(32)

        self.context_select = ContextSelect(self.context_select)

        # Signals setup
        self.ui.connect_signals(self)

        # Properties setup
        self.current_search = ""

    def run(self, theme=None, size=32, context=None):
        self.set_theme(theme)
        self.size_select.set_active_text(size)
        return self.widget.run()

    def get_selected(self):
        path = self.iconview.get_selected_items()[0]
        child_path = self.model_filter.convert_path_to_child_path(path)
        it = self.model.get_iter(child_path)
        return self.model.get(it, self.COLUMN_NAME, self.COLUMN_PATH, self.COLUMN_PIXBUF)

    def set_theme(self, theme):
        self.theme = helpers.get_icon_theme(theme)
        self.context_select.set_theme(self.theme)

    def set_icon_size(self, size=32):
        self.iconsize = size
        width = size > 48 and -1 or (size > 32 and size*3 or 96)
        self.iconview.set_item_width(width)

    def load_icons(self):
        self.model.clear()
        context = self.context_select.get_active_context()
        if 'pixmaps' == context:
            for data_dir in xdg_data_dirs:
                self.load_icons_for_directory(os.path.join(data_dir, 'pixmaps'))
        elif 'all' == context:
            self.load_icons_for_context(context)
            for data_dir in xdg_data_dirs:
                self.load_icons_for_directory(os.path.join(data_dir, 'pixmaps'))
        else:
            self.load_icons_for_context(context)


    def load_icons_for_context(self, context):
        if context == 'all':
            context = None
        icons = self.theme.list_icons(context)
        for icon in icons:
            glib.idle_add(self.load_icon, icon)

    def load_icons_for_directory(self, directory):
        if not os.path.isdir(directory):
            return
        for name in os.listdir(os.path.abspath(directory)):
            path = os.path.join(directory, name)
            if os.path.isfile(path):
                path = os.path.realpath(path)
                if ICON_EXT_RX.match(path):
                    glib.idle_add(self.load_image, path)

    def load_icon(self, name):
        pixbuf = self.theme.load_icon(name, self.iconsize, gtk.ICON_LOOKUP_FORCE_SVG|gtk.ICON_LOOKUP_USE_BUILTIN)
        self.model.append((name, '', pixbuf))

    def load_image(self, path):
        filename = os.path.basename(path)
        name, _ = os.path.splitext(filename)
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(path, self.iconsize, self.iconsize)
        self.model.append((name, path, pixbuf))

    # ---------- SIGNALS

    def on_response(self, dialog, response_id):
        if response_id == gtk.RESPONSE_DELETE_EVENT:
            self.widget.hide()
            return True
        self.widget.hide()
        return False
    
    def on_context_select_changed(self, widget, data=None):
        self.load_icons()

    def on_search_entry_changed(self, widget, data=None):
        self.current_search = self.search_entry.get_text().lower()
        self.model_filter.refilter()

    def on_search_entry_icon_press(self, widget, icon_pos, event, *params):
        self.current_search = ""
        widget.set_text('')

    def on_size_select_changed(self, widget, data=None):
        self.set_icon_size(int(self.size_select.get_active_text()))
        self.load_icons()

    def search_callback(self, model, it, data=None):
        pattern = self.current_search
        if not pattern:
            return True
        name = model.get_value(it, 0)
        if not name:
            return False
        return name.lower().find(pattern) != -1


class IconChooserButton(gobject.GObject):
    __gsignals__ = {
        'file-set': (
            gobject.SIGNAL_RUN_LAST,
            gobject.TYPE_NONE,
            (gobject.TYPE_STRING, gobject.TYPE_STRING)
        )
    }
    def __init__(self, label=None, icon=None, size=24, theme=None, use_underline=True):
        gobject.GObject.__init__(self)

        self.set_theme(theme)
        self.size = size

        self.button = gtk.Button()
        hbox = gtk.HBox()
        self.image = gtk.Image()
        self.label = gtk.Label(label)
        hbox.pack_start(self.image)
        hbox.pack_start(self.label)
        self.button.add(hbox)
        self.button.show_all()
        self.button.connect('clicked', self.on_click)
        self.set_icon(icon)
        self.dialog = IconChooser()

    def set_icon(self, icon):
        pixbuf = None
        if isinstance(icon, str):
            if os.path.isabs(icon):
                pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(icon, self.size, self.size)
            else:
                pixbuf = self.theme.load_icon(icon, self.size, gtk.ICON_LOOKUP_FORCE_SVG|gtk.ICON_LOOKUP_USE_BUILTIN)
        elif isinstance(icon, gtk.gdk.Pixbuf):
            pixbuf = icon
        self.image.set_from_pixbuf(pixbuf)

    def set_theme(self, theme):
        self.theme = helpers.get_icon_theme(theme)

    def set_size(self, size):
        self.image.get_pixbuf().scale_simple(size, size)
        self.size = size

    def on_click(self, widget, data=None):
        response = self.dialog.run(theme=self.theme, size=self.size)
        if gtk.RESPONSE_ACCEPT == response:
            name, path, pixbuf = self.dialog.get_selected()
            pixbuf = pixbuf.scale_simple(self.size, self.size, gtk.gdk.INTERP_BILINEAR)
            self.image.set_from_pixbuf(pixbuf)
            self.label.set_text(name)
            self.emit('file-set', name, path)

gobject.type_register(IconChooserButton)
