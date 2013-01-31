import os
import xdg.IconTheme
import xdg.Mime

import uxm.config as config
import uxm.cache

import gio
import gtk


class IconLookupError(RuntimeError):
    pass


def get_gtk_theme():
    gtk_settings = gtk.settings_get_default()
    return gtk_settings.get_property('gtk-icon-theme-name')


class IconFinder(object):
    """Finds and cache icons"""

    def __init__(self, theme=None, size=24, default_icon=None, cache=None):
        self.theme = theme and theme or get_gtk_theme()
        self.size = size
        self.default_icon = default_icon
        self.cache = cache and cache or uxm.cache.open()
        self.theme_fallbacks = ['gnome', 'oxygen']
        self.symlink_icon = self.find_by_name('emblem-symbolic-link')
        self.symlink_pixbuf = None

    def find_by_name(self, names, default=None):
        """Finds an icon by its name and cache it"""
        if isinstance(names, basestring):
            names = [names]
        if not names:
            names = []
        if default:
            names.append(default)
        elif self.default_icon:
            names.append(self.default_icon)

        for name in names:
            cached = self.cache.find_one_by_name(name, self.theme, self.size)
            if cached:
                return cached['path']
            path = self.lookup(name)
            if path:
                path = self.convert(name, path)
                self.cache.save_icon(name, self.theme, self.size, path)
                return path
        raise IconLookupError("No icon found. Try to adjust the default icon in your config file")

    def find_by_file_path(self, filepath, default='gtk-file'):
        #mime_type = gio.content_type_guess(filepath)
        mime_type = xdg.Mime.get_type(filepath)
        is_link = os.path.islink(filepath)
        return self.find_by_mime_type(str(mime_type), is_link, default)

    def find_by_mime_type(self, mime_type, is_link=False, default='gtk-file'):
        """Finds an icon by its mime type and cache it"""
        cached = self.cache.find_one_by_mime_type(mime_type, self.theme, self.size)
        # found an icon with this mime type
        if cached:
            if is_link:
                if cached['symlink']:
                    return cached['symlink']
                # the cached icon doesn't have a symlink version
                path = self.create_symlink_icon(cached['name'],
                        cached['path'])
                self.cache.update_icon(cached, symlink=path)
                return path
            return cached['path']
        for name in self.content_type_get_choices(mime_type):
            cached = self.cache.find_one_by_name(name, self.theme, self.size)
            # cached icon without associated mime type
            if cached:
                if not is_link:
                    self.cache.update_icon(cached, mimetype=mime_type)
                    return cached['path']
                # now we're looking for a symlink icon
                if cached['symlink']:
                    self.cache.update_icon(cached, mimetype=mime_type)
                    return cached['symlink']
                path = self.create_symlink_icon(cached['name'], cached['path'])
                self.cache.update_icon(cached, mimetype=mime_type,
                        symlink=path)
                return path
            # nothing in the cache, lookup !
            path = self.lookup(name)
            if path:
                if is_link:
                    path, symlink = self.convert(name, path, True)
                    self.cache.save_icon(name, self.theme, self.size, path,
                            symlink, mime_type)
                    return symlink
                path = self.convert(name, path)
                self.cache.save_icon(name, self.theme, self.size, path,
                        mimetype=mime_type)
                return path
        # nothing found, so we return the default
        path = self.find_by_name(default)
        path, symlink = self.convert(default, path, True)
        return is_link and symlink or path


    def get_cache_key(self, name):
        """Compute cache key for name"""
        return "%s_%sx%s_%s" % (
            self.theme, self.size, self.size, name.replace('/', '-')
        )

    def lookup(self, name):
        """Lookup icon by name using xdg.IconTheme"""
        if os.path.isabs(name):
            return name
        path = xdg.IconTheme.getIconPath(name, self.size, self.theme)
        if not path:
            # icon was not found in theme or 'hicolor', try with fallbacks
            for theme in self.theme_fallbacks:
                path = xdg.IconTheme.getIconPath(name, self.size, theme)
                if path:
                    break
        return path

    def convert(self, name, path, symlink=False):
        if path and (path.endswith('.svg') or path.endswith('.xpm')):
            path = self.convert_to_png(name, path)
        if symlink and path:
            symlink_path = self.create_symlink_icon(name, path)
            return (path, symlink_path)
        return path

    def content_type_get_choices(self, mime_type):
        """Returns a list of possible icon names for a given mime type"""
        return gio.content_type_get_icon(mime_type).get_names()
        #parts = mime_type.split('/')
        #t = '-'.join(parts)
        #return [t, 'gnome-mime-%s' % t, '%s-x-generic' % parts[0]]

    def convert_to_png(self, name, path):
        """Converts an icon to png format
        @param str The icon's name
        @param str path A path to an existing icon
        @return gtk.gdk.Pixbuf The path to the converted icon
        """
        #try:
        pixbuf = self.file_to_pixbuf(path)
        filename = os.path.join(config.ICON_CACHE_PATH,
                self.get_cache_key(name) + '.png')
        pixbuf.save(filename, 'png')
        return filename
        #except:
            #return None

    def file_to_pixbuf(self, path):
        return gtk.gdk.pixbuf_new_from_file_at_size(path, self.size, self.size)

    def create_symlink_icon(self, name, icon):
        #try:
        pixbuf = self.get_symlink_pixbuf(icon)
        filename = os.path.join(
            config.ICON_CACHE_PATH,
            self.get_cache_key(name) + '_symlink.png'
        )
        pixbuf.save(filename, 'png')
        return filename
        #except:
            #return None

    def get_symlink_pixbuf(self, icon):
        """Adds a symlink icon on top of the given icon
        @param str or gtk.gdk.Pixbuf icon Path to an icon or an existing gdk.Pixbuf
        @return gtk.gdk.Pixbuf The composited pixbuf
        """
        if isinstance(icon, gtk.gdk.Pixbuf):
            pixbuf = icon.copy()
        else:
            pixbuf = self.file_to_pixbuf(icon)
        if not self.symlink_pixbuf:
            self.symlink_pixbuf = self.file_to_pixbuf(self.symlink_icon)
        w, h = pixbuf.props.width, pixbuf.props.height
        scale = (w / 2.0) / self.symlink_pixbuf.props.width
        self.symlink_pixbuf.composite(
            pixbuf,
            0, 0, w, h,
            w / 2, h / 2, scale, scale,
            gtk.gdk.INTERP_BILINEAR, 255
        )
        return pixbuf
