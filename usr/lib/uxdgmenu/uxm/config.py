import os, optparse, ConfigParser
import cStringIO as StringIO

import xdg.BaseDirectory

import uxm.utils as utils
import uxm.icon_finder as icon_finder

#########################################################
#                                                       #
# -------------------- Config vars -------------------- #
#                                                       #
#########################################################

# These will be replaced by make install
PREFIX = "/usr"
SYSCONFDIR = "/etc"
#

PKG_NAME = "uxdgmenu"
APP_DAEMON = "uxm-daemon"
APP_WATCH = "uxdgmenud"
MENU_FILE = "uxm-applications.menu"
ROOTMENU_FILE = "uxm-rootmenu.menu"

HOME = os.path.expanduser('~')
BOOKMARKS_FILE = os.path.join(HOME, '.gtk-bookmarks')
RECENT_FILES_FILE = os.path.join(HOME, '.recently-used.xbel')

CACHE_DIR = os.path.join(xdg.BaseDirectory.xdg_cache_home, PKG_NAME)
CONFIG_DIR = os.path.join(xdg.BaseDirectory.xdg_config_home, '.config', PKG_NAME)

APP_DIRS = [d for d in xdg.BaseDirectory.load_data_paths('applications')]
DIR_DIRS = [d for d in xdg.BaseDirectory.load_data_paths('desktop-directories')]
MENU_DIRS = [
    os.path.join(SYSCONFDIR, 'xdg', 'menus'),
    os.path.join(CONFIG_DIR, 'menus')
]

SYSTEM_CONFIG_FILE = os.path.join(SYSCONFDIR, PKG_NAME, 'menu.conf')
USER_CONFIG_FILE = os.path.join(CONFIG_DIR, 'menu.conf')

CACHE_DB = os.path.join(CACHE_DIR, 'cache.db')
MENU_CACHE = os.path.join(CACHE_DIR, 'applications')
BOOKMARKS_CACHE = os.path.join(CACHE_DIR, 'bookmarks')
RECENTLY_USED_CACHE = os.path.join(CACHE_DIR, 'recently-used')

PLUGINS_DIRS = [d for d in xdg.BaseDirectory.load_data_paths(PKG_NAME,'formatters')]
PLUGINS_DIRS.append(os.path.join(os.path.dirname(__file__), "formatters"))

# List of directories to monitor
# uxdgmenud will only respond to events on files
# having one of these extensions: .desktop|.directory|.menu
MONITORED = []
MONITORED.extend(DIR_DIRS)
MONITORED.extend(APP_DIRS)
MONITORED.extend(MENU_DIRS)
# List of regex patterns to exclude
# note that theses are C POSIX extended regex patterns,
# so literal special characters must be double escaped !
EXCLUDED = [
    # Debian menu entries
    "/.local/share/applications/menu-xdg/"
]

DEFAULT_CONFIG = """
[General]
filemanager: thunar
terminal: x-terminal-emulator
open_cmd: gnome-open

[Daemon]
monitor_bookmarks: yes
monitor_recent_files: yes

[Applications]
show_all: yes
as_submenu: no

[Bookmarks]

[Recently Used]
max_items: 20

[Places]
start_dir: ~
show_files: yes

[Icons]
show: yes
use_gtk_theme: yes
theme: Mint-X
size: 24
application: application-x-executable
bookmark: user-bookmarks
folder: gtk-directory
file: gtk-file
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
    __parser.set('General', 'open_cmd', open_cmd)
    fm = utils.guess_file_manager()
    __parser.set('General', 'filemanager', fm)
    theme = icon_finder.get_gtk_theme()
    __parser.set('Icons', 'theme', theme)

def to_string():
    buf = StringIO.StringIO()
    __parser.write(buf)
    val = buf.getvalue()
    buf.close()
    return val


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
