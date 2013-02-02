import gtk

import uxm.config as config
import uxm.icon_finder as icon_finder

(
    COLUMN_ID,
    COLUMN_TYPE,
    COLUMN_NAME,
    COLUMN_ICON
) = range(4)

COLUMNS = (int, int, str, gtk.gdk.Pixbuf)

# types are sorted in this order in search results when in MODE_APPS
# in reverse order when in MODE_BROWSE
(
    TYPE_APP,   # an app having a .desktop file
    TYPE_CMD,   # something found in $PATH
    TYPE_FILE,  # a file
    TYPE_DIR,   # a directory or bookmark
    TYPE_DEV    # a device
) = range(5)


class Model(object):

    def __init__(self):
        self.prefs = config.preferences()
        self.default_icon = self.prefs.get('Icons', 'application')
        self.icon_size = self.prefs.getint('Icons', 'size')
        self.use_gtk_theme = self.prefs.getboolean('Icons', 'use_gtk_theme')
        if self.use_gtk_theme:
            self.theme = icon_finder.get_gtk_theme()
        else:
            self.theme = self.prefs.get('Icons', 'theme')
        self.icon_finder = icon_finder.IconFinder(
            self.theme, self.icon_size, self.default_icon
        )
        self.open_cmd = self.prefs.get('General', 'open_cmd')
        self.configure()
        self.new_model()

    def new_model(self):
        self.model = gtk.ListStore(*COLUMNS)

    def get_model(self):
        return self.model

    def configure(self):
        pass
