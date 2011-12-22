import os, optparse, ConfigParser
import cStringIO as StringIO
from . import utils, icon_finder

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

HOME = os.path.expanduser('~')
CACHE_DIR = os.path.join(HOME, '.cache', PKG_NAME)
CONFIG_DIR = os.path.join(HOME, '.config', PKG_NAME)

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
# uxm-watch will only respond to events on files
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
[Places]
show_files: yes
"""

def get():
    """Returns the config parser"""
    return __parser

def check():
    for d in [CONFIG_DIR, CACHE_DIR]:
        if not os.path.isdir(d):
            try:
                os.makedirs(d)
            except OSError, why:
                sys.exit("Could not create %s: %s" % (d, why))
    if not os.path.isfile(USER_CONFIG_FILE):
        guess()
        #with open(CONFIG_FILE, 'w') as f:
            #__parser.write(f)

def guess():
    open_cmd = utils.guess_open_cmd()
    __parser.set('Menu', 'open_cmd', open_cmd)
    fm = utils.guess_file_manager()
    __parser.set('Menu', 'filemanager', fm)
    theme = icon_finder.get_gtk_theme()
    __parser.set('Icons', 'theme', theme)

######################################################
#
__parser = ConfigParser.RawConfigParser()
__parser.readfp(StringIO.StringIO(DEFAULT_CONFIG))
#__parser.read('/etc/marchobmenu/menu.conf')
check()
