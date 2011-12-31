import os, sys, subprocess
from . import config, utils, cache, formatter

############################################
# API
#
def start(opts):
    """starts the daemon"""
    fmt = opts.formatter
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
    cache = get_menu_cache(opts.formatter, 'applications')
    with open(cache, 'r') as f:
        for l in f:
            print l

def update(opts):
    """updates the menu"""
    menu_file = opts.menu_file
    cache = get_menu_cache(opts.formatter, menu_file)
    from uxm.parsers.applications import Parser
    parser = Parser()
    data = parser.parse_menu_file(opts.menu_file)
    fmt = formatter.get_formatter(opts.formatter)
    output = fmt.format_menu(data)
    with open(cache, 'w+') as fp:
        fp.write(output)
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
    fmt = formatter.get_formatter(opts.formatter)
    cache = get_menu_cache(opts.formatter, 'bookmarks')
    from uxm.parsers.bookmarks import Parser
    parser = Parser()
    data = parser.parse_bookmarks()
    output = fmt.format_menu(data)
    with open(cache, 'w+') as fp:
        fp.write(output)

def update_recently_used(opts):
    fmt = formatter.get_formatter(opts.formatter)
    cache = get_menu_cache(opts.formatter, 'recently-used')
    from uxm.parsers.recently_used import Parser
    parser = Parser()
    data = parser.parse_bookmarks()
    output = fmt.format_menu(data)
    with open(cache, 'w+') as fp:
        fp.write(output)

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
    from uxm.parsers.applications import Parser
    clear_cache(opts)
    fmt = formatter.get_formatter(opts.formatter)
    rootmenu = os.path.expanduser(fmt.get_rootmenu_path())
    parser = Parser()
    data = parser.parse_menu_file(config.ROOTMENU_FILE)
    output = fmt.format_rootmenu(data)
    print output
    #with open(rootmenu, 'w+') as fp:
        #fp.write(output)


######################################
# Utilities
#
def get_menu_cache(fmt, menu_file):
    return os.path.join(config.CACHE_DIR, '%s.%s' % (menu_file, fmt.lower()))
