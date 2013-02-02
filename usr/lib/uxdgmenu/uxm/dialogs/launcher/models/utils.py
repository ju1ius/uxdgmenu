import gtk

PIXBUF_CACHE = {}


def load_icon(path, size=24):
    if path in PIXBUF_CACHE:
        return PIXBUF_CACHE[path]
    pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(path, size, size)
    PIXBUF_CACHE[path] = pixbuf
    return pixbuf
