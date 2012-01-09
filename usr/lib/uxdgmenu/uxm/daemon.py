import os, sys, subprocess

import uxm.config as config
import uxm.utils as utils
import uxm.cache as cache
import uxm.formatter as formatter

############################################
# API
#
def start(opts):
    """starts the daemon"""
    fmt = opts.formatter
    stop(opts)
    update(opts)
    cmd = [config.APP_WATCH, '--daemon',
        '--apps-command', '%s update:apps -f %s' % (config.APP_DAEMON, fmt)
    ]
    # Add exclude patterns
    cmd.extend(['--exclude', "|".join(config.EXCLUDED)])
    # Log events
    if opts.verbose:
        cmd.append('--verbose')
    # Gtk Bookmarks
    cfg = config.get()
    if cfg.getboolean('Daemon', 'monitor_bookmarks'):
        cmd.extend([
            '--bookmarks-command',
            '%s update:bookmarks -f %s' % (config.APP_DAEMON, fmt)
        ])
    # Recent Files
    if cfg.getboolean('Daemon', 'monitor_recent_files'):
        cmd.extend([
            '--recent-files-command',
            '%s update:recent-files -f %s' % (config.APP_DAEMON, fmt)
        ])
    # Add monitored dirs
    for d in config.MONITORED:
        cmd.append(d)

    if opts.verbose:
        print "Starting daemon..."
        print cmd
    subprocess.call(cmd)

def stop(opts):
    """stops the daemon"""
    subprocess.call(['pkill', '-u', os.environ['USER'], config.APP_WATCH])

def update(opts):
    cfg = config.get()
    update_applications(opts)
    if cfg.getboolean('Daemon', 'monitor_bookmarks'):
        update_bookmarks(opts)
    if cfg.getboolean('Daemon', 'monitor_recent_files'):
        update_recent_files(opts)

def update_all(opts):
    """Updates all menus"""
    update_applications(opts)
    update_bookmarks(opts)
    update_recent_files(opts)
    update_rootmenu(opts)
    
def update_applications(opts):
    """Updates the applications menu"""
    from uxm.parsers.applications import Parser
    parser = Parser()
    data = parser.parse_menu_file(opts.menu_file)
    fmt = formatter.get_formatter(opts.formatter)
    output = fmt.format_menu(data)
    cache = get_menu_cache(opts.formatter, 'applications')
    with open(cache, 'w+') as fp:
        fp.write(output)

def update_bookmarks(opts):
    from uxm.parsers.bookmarks import Parser
    parser = Parser()
    data = parser.parse_bookmarks()
    fmt = formatter.get_formatter(opts.formatter)
    output = fmt.format_menu(data)
    cache = get_menu_cache(opts.formatter, 'bookmarks')
    with open(cache, 'w+') as fp:
        fp.write(output)

def update_recent_files(opts):
    from uxm.parsers.recent_files import Parser
    parser = Parser()
    data = parser.parse_bookmarks()
    fmt = formatter.get_formatter(opts.formatter)
    output = fmt.format_menu(data)
    cache = get_menu_cache(opts.formatter, 'recent-files')
    with open(cache, 'w+') as fp:
        fp.write(output)

def update_rootmenu(opts):
    from uxm.parsers.rootmenu import Parser
    parser = Parser()
    data = parser.parse_menu_file(config.ROOTMENU_FILE)
    fmt = formatter.get_formatter(opts.formatter)
    output = fmt.format_rootmenu(data)
    cache = get_menu_cache(opts.formatter, 'rootmenu')
    with open(cache, 'w+') as fp:
        fp.write(output)

def clear_cache(opts):
    """Updates the menu and flush the icon cache"""
    try:
        cache.clear()
    except OSError, why:
        sys.exit("Could not remove %s: %s" % (config.CACHE_DB, why))
    update(opts)

def clear_recent_files(opts):
    os.remove(config.RECENT_FILES_FILE) 
    update_recent_files(opts)

def show(opts):
    cache = get_menu_cache(opts.formatter, 'applications')
    with open(cache, 'r') as f:
        for l in f:
            print l

def debug_config(opts):
    print config.to_string()

def debug_applications(opts):
    from pprint import pprint
    from uxm.parsers.applications import Parser
    parser = Parser()
    data = parser.parse_menu_file(opts.menu_file)
    pprint(data)

def debug_bookmarks(opts):
    from pprint import pprint
    from uxm.parsers.bookmarks import Parser
    parser = Parser()
    data = parser.parse_bookmarks()
    pprint(data)

def debug_recent_files(opts):
    from pprint import pprint
    from uxm.parsers.recent_files import Parser
    parser = Parser()
    data = parser.parse_bookmarks()
    pprint(data)

def debug_rootmenu(opts):
    from pprint import pprint
    from uxm.parsers.rootmenu import Parser
    parser = Parser()
    data = parser.parse_menu_file(config.ROOTMENU_FILE)
    pprint(data)

######################################
# Utilities
#
def get_menu_cache(fmt, menu_file):
    return os.path.join(config.CACHE_DIR, '%s.%s' % (menu_file, fmt.lower()))
