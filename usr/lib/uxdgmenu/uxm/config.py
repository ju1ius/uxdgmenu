import os, optparse

class OptionParser(optparse.OptionParser):
    """Custom Option parser for better help formatting"""
    def format_epilog(self, formatter):
        return "\n%s\n" % self.expand_prog_name(self.epilog)

APP_DAEMON = "uxm-daemon"
APP_WATCH = "uxdgmenud"
PKG_NAME = "uxdgmenu"
MENU_FILE = "uxm-applications.menu"
ROOTMENU_FILE = "uxm-rootmenu.menu"
TRIGGERS_DB = "/var/lib/dpkg/triggers/File"

CACHE_DIR = os.path.expanduser('~/.cache/%s' % PKG_NAME)
CONFIG_DIR = os.path.expanduser('~/.config/%s' % PKG_NAME)
for d in [CACHE_DIR, CONFIG_DIR]:
    if not os.path.isdir(d):
        try:
            os.makedirs(d)
        except OSError, why:
            sys.exit("Could not create %s: %s" % (d, why))

SYSTEM_CONFIG_FILE = '/etc/%s/menu.conf' % PKG_NAME
USER_CONFIG_FILE = os.path.join(CONFIG_DIR, 'menu.conf')
CACHE_DB = os.path.join(CACHE_DIR, 'cache.db')
MENU_CACHE = os.path.join(CACHE_DIR, 'applications')
BOOKMARKS_CACHE = os.path.join(CACHE_DIR, 'bookmarks')
RECENTLY_USED_CACHE = os.path.join(CACHE_DIR, 'recently-used')

# List of directories to monitor
# fxm-watch will only respond to events on files
# having one of these extensions: .desktop|.directory|.menu
MONITORED = [
    # .directory files
    "/usr/share/desktop-directories",
    "/usr/local/share/desktop-directories",
    "~/.local/share/desktop-directories",
    # .desktop files
    "/usr/share/applications",
    "/usr/local/share/applications",
    "~/.local/share/applications",
    # .menu files
    "/etc/xdg/menus",
    "~/.config/menus"
]
# List of regex patterns to exclude
# note that theses are C POSIX extended regex patterns,
# so literal special characters must be double escaped !
EXCLUDED = [
    # Debian menu entries
    "/.local/share/applications/menu-xdg/"
]

DEFAULT_CONFIG = """
[Menu]
filemanager: thunar
terminal: x-terminal-emulator -T '%(title)s' -e '%(command)s'
show_all: yes
as_submenu: no
[Recently Used]
max_items: 20
[Icons]
show: yes
use_gtk_theme: yes
theme: Mint-X
size: 24
default: application-default-icon
bookmarks: user-bookmarks
folders: folder
files: gtk-file
"""
