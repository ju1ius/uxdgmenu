import os, sys, subprocess

import uxm.config as config
import uxm.cache as cache
import uxm.formatter as formatter

############################################
# API
#
def start(opts):
    """starts the daemon"""
    opts = options_from_config(opts)
    stop(opts)
    update(opts)
    cmd = [config.APP_WATCH, 'start', '-d']
    # Apps
    if opts.with_applications:
        cmd.append('-a')
    # Gtk Bookmarks
    if opts.with_bookmarks:
        cmd.append('-b')
    # Recent Files
    if opts.with_recent_files:
        cmd.append('-r')
    # Log events
    if opts.verbose:
        cmd.append('-v')
    # Formatter
    cmd.extend(['-f', opts.formatter])

    if opts.verbose:
        print "Starting daemon..."
        print cmd
    subprocess.call(cmd)

def stop(opts):
    """stops the daemon"""
    subprocess.call(['pkill', '-u', os.environ['USER'], config.APP_WATCH])

def update(opts):
    opts = options_from_config(opts)
    if opts.with_applications:
        update_applications(opts)
    if opts.with_bookmarks:
        update_bookmarks(opts)
    if opts.with_recent_files:
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
    menu_cache = get_menu_cache(opts.formatter, 'applications')
    with open(menu_cache, 'w+') as fp:
        fp.write(output)

def update_bookmarks(opts):
    from uxm.parsers.bookmarks import Parser
    parser = Parser()
    data = parser.parse_bookmarks()
    fmt = formatter.get_formatter(opts.formatter)
    output = fmt.format_menu(data)
    menu_cache = get_menu_cache(opts.formatter, 'bookmarks')
    with open(menu_cache, 'w+') as fp:
        fp.write(output)

def update_recent_files(opts):
    from uxm.parsers.recent_files import Parser
    parser = Parser()
    data = parser.parse_bookmarks()
    fmt = formatter.get_formatter(opts.formatter)
    output = fmt.format_menu(data)
    menu_cache = get_menu_cache(opts.formatter, 'recent-files')
    with open(menu_cache, 'w+') as fp:
        fp.write(output)

def update_rootmenu(opts):
    from uxm.parsers.rootmenu import Parser
    parser = Parser()
    data = parser.parse_menu_file(config.ROOTMENU_FILE)
    fmt = formatter.get_formatter(opts.formatter)
    output = fmt.format_rootmenu(data)
    menu_cache = get_menu_cache(opts.formatter, 'rootmenu')
    with open(menu_cache, 'w+') as fp:
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

def options_from_config(opts):
    if (not opts.with_applications and not opts.with_bookmarks and
            not opts.with_recent_files):
        cfg = config.get()
        opts.with_applications = cfg.getboolean(
            'Daemon', 'monitor_applications'
        )
        opts.with_bookmarks = cfg.getboolean(
            'Daemon', 'monitor_bookmarks'
        )
        opts.with_recent_files = cfg.getboolean(
            'Daemon', 'monitor_recent_files'
        )
    return opts

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
