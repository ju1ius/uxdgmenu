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
    cmd = [config.APP_WATCH, 'start']
    cmd_flags = "-D"
    # Apps
    if opts.with_applications:
        cmd_flags += 'a'
    # Gtk Bookmarks
    if opts.with_bookmarks:
        cmd_flags += 'b'
    # Recent Files
    if opts.with_recent_files:
        cmd_flags += 'r'
    # Devices
    if opts.with_devices:
        cmd_flags += 'd'
    # Log events
    if opts.verbose:
        cmd_flags += 'v'
    # Formatter
    cmd.extend([cmd_flags, '-f', opts.formatter])

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
    if opts.with_devices:
        update_devices(opts)

def update_all(opts):
    """Updates all menus"""
    update_applications(opts)
    update_bookmarks(opts)
    update_recent_files(opts)
    update_devices(opts)
    update_rootmenu(opts)
    
def update_applications(opts):
    """Updates the applications menu"""
    from uxm.parsers.applications import Parser
    parser = Parser()
    data = parser.parse_menu_file(opts.menu_file)
    fmt = formatter.get_formatter(opts.formatter)
    output = fmt.format_menu(data)
    menu_cache = get_menu_cache(opts.formatter, config.APPS_CACHE)
    with open(menu_cache, 'w+') as fp:
        fp.write(output)

def update_bookmarks(opts):
    from uxm.parsers.bookmarks import Parser
    parser = Parser()
    data = parser.parse_bookmarks()
    fmt = formatter.get_formatter(opts.formatter)
    output = fmt.format_menu(data)
    menu_cache = get_menu_cache(opts.formatter, config.BOOKMARKS_CACHE)
    with open(menu_cache, 'w+') as fp:
        fp.write(output)

def update_recent_files(opts):
    from uxm.parsers.recent_files import Parser
    parser = Parser()
    data = parser.parse_bookmarks()
    fmt = formatter.get_formatter(opts.formatter)
    output = fmt.format_menu(data)
    menu_cache = get_menu_cache(opts.formatter, config.RECENT_FILES_CACHE)
    with open(menu_cache, 'w+') as fp:
        fp.write(output)

def update_devices(opts):
    from uxm.parsers.devices import Parser
    parser = Parser(opts.formatter)
    data = parser.parse_devices()
    fmt = formatter.get_formatter(opts.formatter)
    output = fmt.format_menu(data)
    menu_cache = get_menu_cache(opts.formatter, config.DEVICES_CACHE)
    with open(menu_cache, 'w+') as fp:
        fp.write(output)

def update_rootmenu(opts):
    from uxm.parsers.rootmenu import Parser
    parser = Parser()
    data = parser.parse_menu_file(config.ROOTMENU_FILE)
    fmt = formatter.get_formatter(opts.formatter)
    output = fmt.format_rootmenu(data)
    menu_cache = get_menu_cache(opts.formatter, config.ROOTMENU_CACHE)
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

def device_mount(dev):
    import uxm.udisks
    uxm.udisks.mount(dev)

def device_unmount(dev):
    import uxm.udisks
    uxm.udisks.unmount(dev)

def device_open(dev):
    import uxm.udisks
    device = uxm.udisks.mount(dev)
    fm = config.preferences().get('General', 'filemanager');
    cmd = [fm, device.mount_paths[0].encode('utf-8')]
    subprocess.call(cmd)


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

def debug_devices(opts):
    from pprint import pprint
    from uxm.parsers.devices import Parser
    parser = Parser()
    data = parser.parse_devices()
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
def options_from_config(opts):
    """When no flags from the command line, fetch config values"""
    if (not opts.with_applications and not opts.with_bookmarks and
            not opts.with_recent_files and not opts.with_devices):
        prefs = config.preferences()
        for p in ['applications','bookmarks','recent_files','devices']:
            setattr(
                opts, "with_%s" % p,
                prefs.getboolean('Daemon', "monitor_%s" % p)
            )
    return opts

def get_menu_cache(fmt, cache_file):
    return '%s.%s' % (cache_file, fmt.lower())
