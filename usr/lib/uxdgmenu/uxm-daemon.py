#! /usr/bin/env python

import os, sys, re, subprocess, optparse

################################################################################
#		CONSTANTS
#-------------------------------------------------------------------------------
APP_PATH = os.path.realpath(__file__)
APP_DIR, APP_DAEMON = os.path.split(APP_PATH)
APP_WATCH = "uxdgmenud"
BUILD_CMD = os.path.join(APP_DIR, 'uxdgmenu.py')

PKG_NAME = "uxdgmenu"
TRIGGERS_DB = "/var/lib/dpkg/triggers/File"

CACHE_DIR = os.path.expanduser('~/.cache/uxdgmenu')
if not os.path.isdir(CACHE_DIR):
    try:
        os.makedirs(CACHE_DIR)
    except OSError, why:
        sys.exit("Could not create %s: %s" % (CACHE_DIR, why))
ICONS_CACHE = os.path.join(CACHE_DIR, 'icons.db')
MENU_CACHE = os.path.join(CACHE_DIR, 'applications')

# List of directories to monitor
MONITORED = [
    # .directory files
    "/usr/share/desktop-directories",
    "/usr/local/share/desktop-directories",
    "~/.local/share/desktop-directories",
    # .desktop files
    "/usr/share/applications",
    "/usr/local/share/applications",
    "~/.local/share/applications",
    # Menu files
    "/etc/xdg/menus",
    "~/.config/menus"
]
# List of regex patterns to exclude
# note that theses are C POSIX extended regex patterns,
# so special characters must be double escaped !
EXCLUDED = [
    # Debian menu entries
    r"/.local/share/applications/menu-xdg/"
]
#-------------------------------------------------------------------------------
#		/CONSTANTS
################################################################################



################################################################################
#		FUNCTIONS
#-------------------------------------------------------------------------------
def start(opts):
    """starts the daemon"""
    stop()
    update(opts)
    cmd = [APP_WATCH, '--daemon',
        '--apps-command', '"%s -w %s update"' % (APP_DAEMON, opts.window_manager)
    ]
    # Add exclude patterns
    cmd.extend(['--exclude', "|".join(EXCLUDED)])
    # Log events
    if opts.verbose:
        cmd.append('--verbose')
    # Add monitored dirs
    for w in MONITORED:
        cmd.append(os.path.expanduser(w))

    if opts.verbose:
        print "Starting daemon..."
        print cmd
    subprocess.call(cmd)

def stop():
    """stops the daemon"""
    subprocess.call(['pkill', '-u', os.environ['USER'], APP_WATCH]);

def update(opts):
    """updates the menu"""
    wm = opts.window_manager
    menu_file = opts.menu_file
    cache = get_menu_cache(wm, menu_file)
    with open(cache, 'w+') as fp:
        fp.write(get_menu(wm, opts.menu_file))

def update_icons(opts):
    """Updates the menu and flush the icon cache"""
    try:
        os.remove(ICONS_CACHE)
        update(opts)
    except OSError, why:
        sys.exit("Could not remove %s: %s" % (ICONS_CACHE, why))

def show(opts):
    """prints the menu to stdout"""
    cache = get_menu_cache(opts.window_manager, opts.menu_file)
    subprocess.call(['cat', cache])


def get_menu(wm, menu_file):
    module_name = 'uxdgmenu.%s' % wm
    try:
        __import__(module_name)
        module = sys.modules[module_name]
        menu = module.Menu(wm)
        return menu.parse_menu_file(menu_file)
    except ImportError, why:
        sys.exit("Window Manager %s not supported (%s)" % (wm, why))

def get_menu_cache(wm, menu_file):
    return os.path.join(CACHE_DIR, '%s-%s' % (wm, menu_file))

#-------------------------------------------------------------------------------
#		/FUNCTIONS
################################################################################



################################################################################
#		MAIN
#-------------------------------------------------------------------------------
if __name__ == '__main__':

    parser = optparse.OptionParser(
        usage="%prog [options] command"        
    )
    parser.add_option(
        '-v', '--verbose', action='store_true',
        help="Verbose"
    )
    parser.add_option(
        '-w', '--window-manager', type='choice',
        choices=[
            'fluxbox','openbox','blackbox','windowmaker','twm','fvwm2','ion3',
            'awesome','icewm','pekwm'
        ],
        help="The window manager for which to generate a menu"
    )
    parser.add_option(
        '-f', '--menu-file', default="uxm-applications.menu",
        help="Choose an alternate menu file. Defaults to 'uxm-applications.menu'"
    )
    ( options, args ) = parser.parse_args()

    if options.verbose:
        print options, args
    if len(args) == 0:
        parser.print_usage()
        sys.exit(1)

    def check_wm():
        if not options.window_manager:
            parser.print_usage()
            sys.exit("You must provide the a valid window manager with this command")

    command = args[0]
    if command == 'start' or command == 'restart':
        check_wm()
        start(options)
    elif command == 'stop':
        stop()
    elif command == 'update':
        check_wm()
        update(options)
    elif command == 'show':
        check_wm()
        show(options)
    elif command == 'update-icons':
        check_wm()
        update_icons(options)
    else:
        parser.print_usage()
        sys.exit(1)
