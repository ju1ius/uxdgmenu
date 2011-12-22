#! /usr/bin/env python

import os, sys
import uxm.config as config
import uxm.daemon as daemon
import uxm.utils as utils


def check_wm(fatal=True):
    if not options.window_manager:
        if fatal:
            parser.print_usage()
            sys.exit("You must provide the a valid window manager with this command")
        else:


if __name__ == '__main__':
    usage = "%prog [options] command"
    description = """Commands:
  help                  prints the help message and exits
  start                 starts the menu daemon
  stop                  stops the menu daemon
  update                regenerates the applications menu
  update-bookmarks      regenerates the bookmarks menu
  update-recently-used  regenerates the recently used files menu
  clear-recently-used   clears the recently used files menu
  clear-cache           regenerates the icon cache,
                        then updates applications, bookmarks,
                        and recently used files menus.
  generate-rootmenu     generates a rootmenu
"""
    
    parser = config.OptionParser(
        usage = usage, epilog = description      
    )
    parser.add_option(
        '-v', '--verbose', action='store_true',
        help="be verbose and log inotify events to syslog"
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
        '-d', '--detect', action='store_true',
        help="Tries to detect the current window manager"
    )
    parser.add_option(
        '-f', '--menu-file', default="uxm-applications.menu",
        help="Choose an alternate menu file. Defaults to 'uxm-applications.menu'"
    )
    parser.add_option(
        '-a', '--all', action='store_true',
        help="equivalent to -br"
    )
    parser.add_option(
        '-b', '--with-bookmarks', action='store_true',
        help="monitor GTK bookmarks"
    )
    parser.add_option(
        '-r', '--with-recently-used', action='store_true',
        help="monitor recently used files"
    )
    parser.add_option(
        '-p', '--progress', action='store_true',
        help="display a progress bar if zenity is installed"
    )
    ( options, args ) = parser.parse_args()

    if len(args) == 0:
        parser.print_usage()
        sys.exit(1)

    if options.verbose:
        import time
        start_t = time.clock()

    if options.progress:
        if not utils.which('zenity'):
            options.progress = False
        else:
            progress_opts = utils.get_options_for_progress(options)

    if options.all:
        options.with_bookmarks = True
        options.with_recently_used = True

    if options.detect:
        wms = ['fluxbox','openbox','blackbox','windowmaker','twm','fvwm2','ion3', 'awesome','icewm','pekwm']
        pattern = "^(%s)$" % "|".join(wms)
        pids = utils.pgrep(pattern, user=os.environ['USER'], name=True)
        if pids:
            # There should be only one WM for the same user
            options.window_manager = pids[0][1]

    command = args[0]
    if command == 'start' or command == 'restart':
        check_wm()
        daemon.start(options)
    elif command == 'stop':
        daemon.stop()
    elif command == 'update':
        check_wm()
        if options.progress:
            import uxm.dialogs.progress as progress
            def update():
                daemon.update(options)
            progress.indeterminate(
                "Progress ;-)",
                update
            )
            #utils.zenity_progress(command, progress_opts)
        else:
            daemon.update(options)
    elif command == 'update-bookmarks':
        check_wm()
        if options.progress:
            utils.zenity_progress(command)
        else:
            daemon.update_bookmarks()
    elif command == 'update-recently-used':
        check_wm()
        if options.progress:
            utils.zenity_progress(command)
        else:
            daemon.update_recently_used()
    elif command == 'clear-recently-used':
        check_wm()
        if options.progress:
            utils.zenity_progress(command)
        else:
            daemon.clear_recently_used()
    elif command == 'generate-rootmenu':
        check_wm()
        if options.progress:
            utils.zenity_progress(command)
        else:
            daemon.generate_rootmenu()
    elif command == 'clear-cache':
        if options.progress:
            utils.zenity_progress(command)
        else:
            daemon.clear_cache()
    elif command == 'enable-triggers':
        daemon.enable_triggers()
    elif command == 'disable-triggers':
        daemon.disable_triggers()
    else:
        parser.print_help()
        sys.exit(1)

    if options.verbose:
        end_t = time.clock()
        print "Executed in %s seconds" % str(end_t - start_t)

    sys.exit(0)
