import gtk, gobject

def get_icon_theme(name):
    if isinstance(name, gtk.IconTheme):
        return name
    theme = gtk.IconTheme()
    if not name:
        settings = gtk.settings_get_default()
        name = settings.get_property('gtk-icon-theme-name')
    theme.set_custom_theme(name)
    return theme

class BuildableWidgetDecorator(object):

    def __init__(self, ui_file, name):
        self.ui = gtk.Builder()
        self.ui.add_from_file(ui_file)
        self.widget = self.ui.get_object(name)

    def add_ui_widget(self, name):
        setattr(self, name, self.ui.get_object(name))

    def add_ui_widgets(self, *names):
        for name in names:
            self.add_ui_widget(name)

    def connect_signals(self):
        self.ui.connect_signals(self)
            
    def __getattr__(self, name):
        return getattr(self.widget, name)

class WidgetDecorator(object):

    def __init__(self, widget):
        self.widget = widget

    def __getattr__(self, name):
        return getattr(self.widget, name)

class ComboBoxTextDecorator(WidgetDecorator):
    """Decorator for simple text comboboxes"""
    def __init__(self, widget):
        super(ComboBoxTextDecorator, self).__init__(widget)
        self.model = gtk.ListStore(gobject.TYPE_STRING)
        self.widget.set_model(self.model)
        cell = gtk.CellRendererText()
        self.widget.pack_start(cell, True)
        self.widget.add_attribute(cell, 'text', 0)

    def append_text(self, text):
        self.model.append([str(text)])

    def get_active_text(self):
        i = self.widget.get_active()
        row = self.model[i]
        return row[0]

    def set_active_text(self, text):
        text = str(text)
        for i, row in enumerate(self.model):
            if row[0] == text:
                self.widget.set_active(i)
