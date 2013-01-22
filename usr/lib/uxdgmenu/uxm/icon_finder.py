import os
import xdg.IconTheme
import xdg.Mime

import uxm.config as config
import uxm.cache

try:
    import gio
    HAS_GIO = True
except:
    HAS_GIO = False

try:
    import pygtk
    pygtk.require('2.0')
    import gtk
    HAS_GTK = True
except:
    HAS_GTK = False

def get_gtk_theme():
    if HAS_GTK:
        gtk_settings = gtk.settings_get_default()
        return gtk_settings.get_property('gtk-icon-theme-name')

class IconFinder(object):
    """Finds and cache icons"""

    def __init__(self, theme=None, size=24, default_icon=None, cache=None):
        self.theme = theme and theme or get_gtk_theme()
        self.size = size
        self.default_icon = default_icon
        self.cache = cache and cache or uxm.cache.Cache().open()
        self.theme_fallbacks = ['gnome', 'oxygen']

    def find_by_name(self, names, default=None):
        if isinstance(names, basestring):
            names = [names]
        if default:
            names.append(default)
        elif self.default_icon:
            names.append(self.default_icon)
        for name in names:
            """Finds an icon by its name and cache it"""
            cached = self.lookup_cache(name)
            if cached:
                return cached['path'].encode('utf-8')
            path = self.lookup(name)
            if path:
                self.cache_icon(name, path)
                return path.encode('utf-8')

    def find_by_mime_type(self, mime_type, default='gtk-file'):
        """Finds an icon by its mime type and cache it"""
        return self.find_by_name(
            self.content_type_get_choices(mime_type),
            default
        )

    def find_by_file_path(self, filepath, default='gtk-file'):
        #if HAS_GIO:
            #mime_type = gio.content_type_guess(filepath)
        #else:
        mime_type = xdg.Mime.get_type(filepath)
        return self.find_by_mime_type(str(mime_type), default)

    def get_cache_key(self, name):
        """Compute cache key for name"""
        return "%s_%sx%s_%s" % (
            self.theme, self.size, self.size, name
        )

    def lookup(self, name):
        """Lookup icon by name using xdg.IconTheme"""
        path = xdg.IconTheme.getIconPath(name, self.size, self.theme)
        if not path:
            # icon was not found in theme or 'hicolor', try with fallbacks
            for theme in self.theme_fallbacks:
                path = xdg.IconTheme.getIconPath(name, self.size, theme)
                if path:
                    break
        if path and (path.endswith('.svg') or path.endswith('.xpm')):
            return self.convert_to_png(name, path)
        return path

    def lookup_cache(self, name):
        return self.cache.get_icon(name, self.theme, self.size)

    def cache_icon(self, name, path):
        self.cache.add_icon(name, self.theme, self.size, path)

    def content_type_get_choices(self, mime_type):
        """Returns a list of possible icon names for a given mime type"""
        if HAS_GIO:
            return gio.content_type_get_icon(mime_type).get_names()
        else:
            parts = mime_type.split('/')
            t = '-'.join(parts)
            return [t, 'gnome-mime-%s' % t, '%s-x-generic' % parts[0]]

    def convert_to_png(self, name, path):
        pixbuf = gtk.gdk.pixbuf_new_from_file(path)
        pixbuf = pixbuf.scale_simple(self.size, self.size, gtk.gdk.INTERP_HYPER)
        filename = os.path.join(config.ICON_CACHE_PATH, self.get_cache_key(name))
        try:
            pixbuf.save(filename, 'png')
            return filename
        except:
            return None
