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
  help                  Prints the help message and exits

  start                 Starts the menu daemon
                        If none of -a, -b or -r are provided,
                        use options specified in the config file
  stop                  Stops the menu daemon

  update                Regenerates menus
                        If none of -a, -b or -r are provided,
                        use options specified in the config file
  update:all            Regenerates all menus
  update:applications   Regenerates the applications menu
                        Equivalent to uxm-daemon:update -a
  update:apps           Alias for update:applications
  update:bookmarks      Regenerates the bookmarks menu
                        Equivalent to uxm-daemon:update -b
  update:recent-files   Regenerates the recent files menu
                        Equivalent to uxm-daemon:update -r
  update:rootmenu       Regenerates the rootmenu

  clear:recent-files    Clears and regenerates the recent files menu
  clear:cache           Clears the icon cache, then regenerates menus

  debug:config          Outputs the computed config values
  debug:applications    Outputs a representation of the parsed data
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
        '-a', '--with-applications', action='store_true',
        help="Monitor / update applications"
    )
    parser.add_option(
        '-b', '--with-bookmarks', action='store_true',
        help="Monitor / update GTK bookmarks"
    )
    parser.add_option(
        '-r', '--with-recent-files', action='store_true',
        help="Monitor / update recent files"
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
