import os, optparse, ConfigParser
import cStringIO as StringIO

from . import utils, icon_finder

#########################################################
#                                                       #
# -------------------- Config vars -------------------- #
#                                                       #
#########################################################

# These two might be replaced by make install
PREFIX = "/usr"
SYSCONFDIR = "/etc"
#

PKG_NAME = "uxdgmenu"
APP_DAEMON = "uxm-daemon"
APP_WATCH = "uxdgmenud"
MENU_FILE = "uxm-applications.menu"
ROOTMENU_FILE = "uxm-rootmenu.menu"

HOME = os.path.expanduser('~')
CACHE_DIR = os.path.join(HOME, '.cache', PKG_NAME)
CONFIG_DIR = os.path.join(HOME, '.config', PKG_NAME)

SYSTEM_CONFIG_FILE = os.path.join(SYSCONFDIR, PKG_NAME, 'menu.conf')
USER_CONFIG_FILE = os.path.join(CONFIG_DIR, 'menu.conf')

CACHE_DB = os.path.join(CACHE_DIR, 'cache.db')
MENU_CACHE = os.path.join(CACHE_DIR, 'applications')
BOOKMARKS_CACHE = os.path.join(CACHE_DIR, 'bookmarks')
RECENTLY_USED_CACHE = os.path.join(CACHE_DIR, 'recently-used')

PLUGINS_DIRS = [
    os.path.expanduser('~/.local/share/%s/formatters' % PKG_NAME),
    os.path.join(PREFIX,'share',PKG_NAME,'formatters'),
    os.path.join(os.path.dirname(__file__), "formatters"),
]

# List of directories to monitor
# uxdgmenud will only respond to events on files
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
terminal: x-terminal-emulator
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
folders: gtk-directory
files: gtk-file
[Places]
show_files: yes
"""

############################################################
#                                                          #
# -------------------- Config methods -------------------- #
#                                                          #
############################################################


class OptionParser(optparse.OptionParser):
    """Custom Option parser for better help formatting"""
    def format_epilog(self, formatter):
        return "\n%s\n" % self.expand_prog_name(self.epilog)

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


########################################################
#                                                      #
# -------------------- Config Run -------------------- #
#                                                      #
########################################################

# Parse uxdgmenu default config
__parser = ConfigParser.RawConfigParser()
__parser.readfp(StringIO.StringIO(DEFAULT_CONFIG))
# Create working dirs & config files if needed
check()
# Parse config files
#__parser.read([SYSTEM_CONFIG_FILE, USER_CONFIG_FILE])
