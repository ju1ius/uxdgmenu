import gtk

COLUMNS = (int, int, str, gtk.gdk.Pixbuf)

(
    TYPE_APP,
    TYPE_FILE,
    TYPE_DIR,
    TYPE_DEV
) = range(4)

(
    COLUMN_ID,
    COLUMN_TYPE,
    COLUMN_NAME,
    COLUMN_ICON
) = range(4)

(
    MODE_APPS,
    MODE_BROWSE
) = range(2)

PIXBUF_CACHE = {}


def load_icon(path, size=24):
    if path in PIXBUF_CACHE:
        return PIXBUF_CACHE[path]
    else:
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(path, size, size)
        PIXBUF_CACHE[path] = pixbuf
        return pixbuf
