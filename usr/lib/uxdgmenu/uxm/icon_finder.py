import os
import xdg.IconTheme as IconTheme
import xdg.Mime

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

    def __init__(self, theme, size, default_icon, cache):
        self.theme = theme
        self.size = size
        self.default_icon = default_icon
        self.cache = cache

    def find_by_name(self, name):
        """Finds an icon by its name and cache it"""
        if not name:
            name = self.default_icon
        cache_key = self.icon_name_get_cache_key(name)      
        cached = self.cache.get_icon(cache_key)
        if cached:
            return cached['path'].encode('utf-8')
        else:
            path = self.lookup(name)
            if path:
                self.cache.add_icon(cache_key, path)
                return path.encode('utf-8')
            return self.lookup(self.default_icon).encode('utf-8')

    def find_by_mime_type(self, mime_type, default='gtk-file'):
        """Finds an icon by its mime type and cache it"""
        for name in self.content_type_get_choices(mime_type):
            cache_key = self.icon_name_get_cache_key(name)      
            cached = self.cache.get_icon(cache_key)
            if cached:
                return cached['path'].encode('utf-8')
            else:
                path = self.lookup(name)
                if path:
                    self.cache.add_icon(cache_key, path)
                    return path.encode('utf-8')
        return self.lookup(default).encode('utf-8')

    def find_by_file_path(self, filepath):
        #if HAS_GIO:
            #mime_type = gio.content_type_guess(filepath)
        #else:
        mime_type = xdg.Mime.get_type(filepath)
        return self.find_by_mime_type(str(mime_type))

    def icon_name_get_cache_key(self, name):
        """Compute cache key for name"""
        if not name:
            name = self.default_icon
        if os.path.isabs(name):
            return name
        return name + '::' + self.theme

    def lookup(self, name):
        """Lookup icon by name using xdg.IconTheme"""
        # Use xdg.IconTheme icon lookup, omitting svg icons
        path = IconTheme.getIconPath(
            name, self.size, self.theme, ['png','xpm']
        )
        if path and not path.endswith('.svg'):
            return path

    def content_type_get_choices(self, mime_type):
        """Returns a list of possible icon names for a given mime type"""
        if HAS_GIO:
            return gio.content_type_get_icon(mime_type).get_names()
        else:
            parts = mime_type.split('/')
            t = '-'.join(parts)
            return [t, 'gnome-mime-%s' % t, '%s-x-generic' % parts[0]]
