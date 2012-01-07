#! /usr/bin/env python

import os, sys
import uxm.config as config
import uxm.daemon as daemon
import uxm.utils as utils


def check_formatter(fatal=True):
    if not options.formatter:
        if fatal:
            parser.print_usage()
            sys.exit("You must provide a valid formatter with this command")
        else:
            pass

def progress_dialog(msg, func, *args, **kwargs):
    import uxm.dialogs.progress as progress
    progress.indeterminate(msg, func, *args, **kwargs)

def die():
    parser.print_help()
    sys.exit(1)


if __name__ == '__main__':
    usage = "%prog [options] command"
    description = """Commands:
  help                  prints the help message and exits

  start                 starts the menu daemon
  stop                  stops the menu daemon

  update                regenerates menus specified in the config file
  update:all            regenerates all menus
  update:applications   regenerates the applications menu
  update:apps           alias for update:applications
  update:bookmarks      regenerates the bookmarks menu
  update:recent-files   regenerates the recent files menu
  update:rootmenu       regenerates the rootmenu

  clear:recent-files    clears and regenerates the recent files menu
  clear:cache           clears the icon cache, then regenerates menus

  debug:config          outputs the computed config values
  debug:applications    outputs a representation of the parsed data
  debug:bookmarks
  debug:recent-files
  debug:rootmenu

"""
    
    parser = config.OptionParser(
        usage = usage, epilog = description      
    )
    parser.add_option(
        '-v', '--verbose', action='store_true',
        help="be verbose and log inotify events to syslog"
    )
    parser.add_option(
        '-f', '--formatter', default="pckl",
        help="The formatter for the menu"
    )
    parser.add_option(
        '-m', '--menu-file', default="uxm-applications.menu",
        help="""Choose an alternate applications menu file.
Defaults to 'uxm-applications.menu'"""
    )
    parser.add_option(
        '-p', '--progress', action='store_true',
        help="Display a GTK progress bar dialog"
    )
    ( options, args ) = parser.parse_args()

    if len(args) == 0:
        die()

    if options.verbose:
        import time
        start_t = time.clock()

    command = args[0].split(':')

    if len(command) == 1:
        action = command[0]
        if action == 'restart':
            action = 'start'
    else:
        ns, action = command[0:2]
        if ns == 'update':
            if action == 'apps':
                action = 'applications'
        action = "_".join([ns, action])

    try:
        action = getattr(daemon, action.replace('-', '_'))
    except:
        die()

    if options.progress:
        progress_dialog("", action, options)
    else:
        action(options)

    if options.verbose:
        end_t = time.clock()
        print "Executed in %s seconds" % str(end_t - start_t)

    sys.exit(0)
