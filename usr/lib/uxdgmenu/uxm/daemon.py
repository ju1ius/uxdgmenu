import os
import sys
import subprocess
import multiprocessing
import multiprocessing.pool
import logging

import uxm.config as config
import uxm.cache as cache
import uxm.formatter


logger = logging.getLogger('uxm-daemon')


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

    logger.debug("Starting: %s", cmd)
    subprocess.call(cmd)


def stop(opts):
    """stops the daemon"""
    logger.debug("Stopping")
    subprocess.call(['pkill', '-u', os.environ['USER'], config.APP_WATCH])


def update(opts):
    opts = options_from_config(opts)
    actions = []
    if opts.with_applications:
        actions.append(update_applications)
    if opts.with_bookmarks:
        actions.append(update_bookmarks)
    if opts.with_recent_files:
        actions.append(update_recent_files)
    if opts.with_devices:
        actions.append(update_devices)
    num_actions = len(actions)
    if num_actions == 1:
        actions[0](opts)
    else:
        pool = NoDaemonPool(processes=num_actions)
        for action in actions:
            pool.apply_async(action, (opts, True))
        pool.close()
        pool.join()


def update_all(opts):
    """Updates all menus"""
    pool = NoDaemonPool(processes=5)
    pool.apply_async(update_applications, (opts,))
    pool.apply_async(update_bookmarks, (opts,))
    pool.apply_async(update_recent_files, (opts,))
    pool.apply_async(update_devices, (opts,))
    pool.apply_async(update_rootmenu, (opts,))
    pool.close()
    pool.join()


def update_applications(opts, is_process=False):
    """Updates the applications menu"""
    logger.debug('Updating applications')
    from uxm.parsers.applications import Parser
    parser = Parser()
    func = lambda: parser.parse_menu_file(opts.menu_file)
    update_wrapper(func, opts, config.APPS_CACHE)


def update_bookmarks(opts, is_process=False):
    logger.debug('Updating bookmarks')
    from uxm.parsers.bookmarks import Parser
    parser = Parser()
    func = lambda: parser.parse_bookmarks()
    update_wrapper(func, opts, config.BOOKMARKS_CACHE)


def update_recent_files(opts, is_process=False):
    logger.debug('Updating recent_files')
    from uxm.parsers.recent_files import Parser
    parser = Parser()
    func = lambda: parser.parse_bookmarks()
    update_wrapper(func, opts, config.RECENT_FILES_CACHE)


def update_devices(opts, is_process=False):
    logger.debug('Updating devices')
    from uxm.parsers.devices import Parser
    parser = Parser(opts.formatter)
    func = lambda: parser.parse_devices()
    update_wrapper(func, opts, config.DEVICES_CACHE)


def update_rootmenu(opts, is_process=False):
    logger.debug('Updating rootmenu')
    from uxm.parsers.rootmenu import Parser
    parser = Parser()
    func = lambda: parser.parse_menu_file(config.ROOTMENU_FILE)
    update_wrapper(func, opts, config.ROOTMENU_CACHE)


def update_wrapper(parse_func, opts, cache_file):
    data = parse_func()
    formatters = opts.formatter.split(',')
    if len(formatters) == 1:
        format_and_write(formatters[0], data, cache_file)
    else:
        format_and_write_async(formatters, data, cache_file)


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
    fm = config.preferences().get('General', 'filemanager')
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
        for p in ('applications', 'bookmarks', 'recent_files', 'devices'):
            setattr(
                opts, "with_%s" % p,
                prefs.getboolean('Daemon', "monitor_%s" % p)
            )
    return opts


def get_menu_cache(fmt, cache_file):
    return '%s.%s' % (cache_file, fmt.lower())


def format_and_write(formatter, data, cache_file):
    fmt = uxm.formatter.get_formatter(formatter)
    output = fmt.format_menu(data)
    menu_cache = get_menu_cache(formatter, cache_file)
    logger.debug('Writing data in %s' % menu_cache)
    with open(menu_cache, 'w+') as fp:
        fp.write(output)


def format_and_write_async(formatters, data, cache_file):
    pool = multiprocessing.Pool(processes=len(formatters))
    for f in formatters:
        pool.apply_async(format_and_write, (f, data, cache_file))
    pool.close()
    pool.join()


class NoDaemonProcess(multiprocessing.Process):

    # make 'daemon' attribute always return False
    def _get_daemon(self):
        return False

    def _set_daemon(self, value):
        pass

    daemon = property(_get_daemon, _set_daemon)


# We sub-class multiprocessing.pool.Pool instead of multiprocessing.Pool
# because the latter is only a wrapper function, not a proper class.
class NoDaemonPool(multiprocessing.pool.Pool):
    Process = NoDaemonProcess
