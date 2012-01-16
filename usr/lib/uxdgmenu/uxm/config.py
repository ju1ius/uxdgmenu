import os, sys, optparse, ConfigParser
import cStringIO as StringIO

import xdg.BaseDirectory

import uxm.utils as utils
import uxm.icon_finder as icon_finder



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
        with open(USER_CONFIG_FILE, 'w') as f:
            __parser.write(f)

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

__ugettext = None

def translate(*args, **kwargs):
    global __ugettext
    if __ugettext is None:
        import gettext
        t = gettext.translation("uxdgmenu", os.path.join(PREFIX,"share/locale"))
        __ugettext = t.ugettext
    return __ugettext(*args, **kwargs)

def get_recent_files_path():
    path = os.path.join(HOME, '.recently-used.xbel')
    if os.path.exists(path):
        return path
    return os.path.join(xdg.BaseDirectory.xdg_data_home, 'recently-used.xbel')



#########################################################
#                                                       #
# ------------------ Config constants ----------------- #
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
RECENT_FILES_FILE = get_recent_files_path()

CACHE_DIR = os.path.join(xdg.BaseDirectory.xdg_cache_home, PKG_NAME)
CONFIG_DIR = os.path.join(xdg.BaseDirectory.xdg_config_home, PKG_NAME)

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
RECENT_FILES_CACHE = os.path.join(CACHE_DIR, 'recent-files')

PLUGINS_DIRS = [d for d in xdg.BaseDirectory.load_data_paths(PKG_NAME,'formatters')]
PLUGINS_DIRS.append(os.path.join(os.path.dirname(__file__), "formatters"))

DEFAULT_CONFIG = """
[General]
filemanager: thunar
terminal: x-terminal-emulator
open_cmd: gnome-open

[Daemon]
monitor_applications: yes
monitor_bookmarks: yes
monitor_recent_files: yes
monitor_devices: yes

[Applications]
menu_file: uxm-applications.menu
show_all: yes
as_submenu: no

[Bookmarks]

[Recent Files]
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

internal_drive: gtk-harddisk
optical_drive: gtk-cdrom
removable_drive: gnome-dev-removable
mount: gtk-execute
unmount: media-eject
"""         

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
__parser.read([SYSTEM_CONFIG_FILE, USER_CONFIG_FILE])
