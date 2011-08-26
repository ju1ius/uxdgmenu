#! /usr/bin/env python

import os, sys, optparse
import uxm.places, uxm.utils

if __name__ == "__main__":
    usage = """%prog window_manager start_directory"""
    parser = optparse.OptionParser(usage=usage)
    parser.add_option(
        '-f', '--file-manager',
        help="The file manager to use for opening files"
    )
    parser.add_option(
        '-s', '--show-files', action="store_true",
        help="Do we show files ?"
    )
    options, args = parser.parse_args()
    
    if len(args) < 2:
        parser.print_help()
        sys.exit(1)

    if not options.file_manager:
        options.file_manager = uxm.utils.get_default_filemanager()

    path = os.path.abspath(os.path.expanduser(args[1]))
    menu = uxm.places.PlacesMenu(args[0])
    menu.file_manager = options.file_manager
    print menu.parse_path(path, options.show_files)
