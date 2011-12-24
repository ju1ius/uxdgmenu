import os, sys, subprocess
from . import config, utils, cache

############################################
# API
#
def start(opts):
    """starts the daemon"""
    fmt = opts.formatter
    check_triggers()
    stop()
    update(opts)
    cmd = [config.APP_WATCH, '--daemon',
        '--apps-command', '%s update -f %s' % (config.APP_DAEMON, fmt)
    ]
    # Add exclude patterns
    cmd.extend(['--exclude', "|".join(config.EXCLUDED)])
    # Log events
    if opts.verbose:
        cmd.append('--verbose')
    # Gtk Bookmarks
    if opts.with_bookmarks:
        cmd.extend([
            '--bookmarks-command',
            '%s update-bookmarks -f %s' % (config.APP_DAEMON, fmt)
        ])
    # Recently Used items
    if opts.with_recently_used:
        cmd.extend([
            '--recently-used-command',
            '%s update-recently-used -f %s' % (config.APP_DAEMON, fmt)
        ])
    # Add monitored dirs
    for d in config.MONITORED:
        cmd.append(os.path.expanduser(d))

    if opts.verbose:
        print "Starting daemon..."
        print cmd
    subprocess.call(cmd)

def stop():
    """stops the daemon"""
    subprocess.call(['pkill', '-u', os.environ['USER'], config.APP_WATCH])

def show(opts):
    fmt = opts.formatter
    cache = get_menu_cache(fmt, 'applications')
    with open(cache, 'r') as f:
        for l in f:
            print l

def update(opts):
    """updates the menu"""
    fmt = opts.formatter
    menu_file = opts.menu_file
    cache = get_menu_cache(fmt, menu_file)
    formatter = get_formatter(fmt)
    from uxm.parsers.applications import Parser
    parser = Parser()
    data = parser.parse_menu_file(opts.menu_file)
    with open(cache, 'w+') as fp:
        fp.write(formatter.format_menu(data))
    if opts.with_bookmarks:
        update_bookmarks(opts)
    if opts.with_recently_used:
        update_recently_used(opts)

def clear_cache(opts):
    """Updates the menu and flush the icon cache"""
    try:
        cache.clear()
    except OSError, why:
        sys.exit("Could not remove %s: %s" % (config.CACHE_DB, why))
    update(opts)
    update_bookmarks(opts)
    update_recently_used(opts)

def update_bookmarks(opts):
    fmt = opts.formatter
    formatter = get_formatter(fmt)
    cache = get_menu_cache(fmt, 'bookmarks')
    from uxm.parsers.bookmarks import Parser
    parser = Parser()
    data = parser.parse_bookmarks()
    with open(cache, 'w+') as fp:
        fp.write(formatter.format_menu(data))

def update_recently_used(opts):
    fmt = opts.formatter
    formatter = get_formatter(fmt)
    cache = get_menu_cache(fmt, 'recently_used')
    from uxm.parsers.recently_used import Parser
    parser = Parser()
    data = parser.parse_bookmarks()
    with open(cache, 'w+') as fp:
        fp.write(formatter.format_menu(data))

def clear_recently_used(opts):
    with open(os.path.expanduser('~/.recently-used.xbel'), 'w') as f:
        f.write("""<?xml version="1.0" encoding="UTF-8"?>
<xbel version="1.0"
      xmlns:bookmark="http://www.freedesktop.org/standards/desktop-bookmarks"
      xmlns:mime="http://www.freedesktop.org/standards/shared-mime-info"
>
</xbel>""")
    update_recently_used(opts)

def generate_rootmenu(opts):
    clear_cache(opts)
    update_bookmarks(opts)
    update_recently_used(opts)
    rootmenu = os.path.expanduser('~/.fluxbox/menu')
    if os.path.isfile(rootmenu):
        try:
            os.rename(rootmenu, "%s.bak" % rootmenu)
        except OSError, why:
            sys.exit("Could not backup previous rootmenu: %s" % why)
    fmt = opts.formatter
    formatter = get_formatter(fmt)
    from uxm.parsers.rootmenu import Parser
    parser = Parser()
    data = parser.parse_menu_file(config.ROOTMENU_FILE)
    with open(rootmenu, 'w+') as fp:
        fp.write(formatter.format_rootmenu(data))

def disable_triggers():
    if not os.path.isfile(config.TRIGGERS_DB):
        sys.exit("Your system doesn't support dpkg-triggers. Please use the daemon instead.")
    subprocess.call(
        'sudo sed -i -e "/%s$/d" %s' % (config.PKG_NAME, config.TRIGGERS_DB),
        shell=True
    )

def enable_triggers():
    """Add dpkg interests for the monitored directories
        If the directory is in userspace (under '~'),
        we attempt to add an interest for all existing real users."""
    if not os.path.isfile(config.TRIGGERS_DB):
        sys.exit("Your system doesn't support dpkg-triggers. Please use the daemon instead.")
    stop()
    disable_triggers()
    interests = []
    for d in config.MONITORED:
        if d.startswith('~'):
            for (user, home) in utils.list_real_users():
                interests.append(d.replace('~', home, 1))
        else:
            interests.append(d)
    for i in interests:
        subprocess.call(
            "echo %s %s | sudo tee -a %s" % (
                i, config.PKG_NAME, config.TRIGGERS_DB
            ),
            shell=True
        )

def check_triggers():
    """Checks for presence of dpkg-triggers"""
    r = subprocess.call(
        "grep %s %s > /dev/null" % (config.PKG_NAME, config.TRIGGERS_DB),
        shell=True
    )
    if r == 0:
        print """
It seems you have dpkg-triggers running for %(p)s !
You must disable them before starting the daemon by running:
    %(d)s disable-triggers
If you want to know more about dpkg-triggers, run:
    %(d)s --help
""" % { "p": config.PKG_NAME, "d": config.APP_DAEMON }
        sys.exit(1)


######################################
# Utilities
#
def get_formatter(name):
    import uxm.formatters
    try:
        return uxm.formatters.get_formatter(name)
    except ImportError, why:
        sys.exit("No Formatter named %s (%s)" % (fmt, why))

def get_menu_cache(fmt, menu_file):
    return os.path.join(config.CACHE_DIR, '%s.%s' % (menu_file, fmt))
