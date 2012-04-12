#! /usr/bin/python

import os, sys, optparse

from uxm.parsers.places import Parser
import uxm.config
import uxm.formatter

if __name__ == "__main__":
    usage = """%prog [options] start_directory"""
    parser = optparse.OptionParser(usage=usage)
    parser.add_option(
        '-f', '--formatter',
        help="The formatter for the menu"
    )
    options, args = parser.parse_args()

    if not options.formatter:
        parser.print_usage()
        sys.exit(1)
    
    if len(args) < 1:
        start_dir = uxm.config.preferences().get('Places', 'start_dir')
    else:
        start_dir = args[0]

    path = os.path.expanduser(start_dir)
    parser = Parser(options.formatter)
    data = parser.parse_path(path)
    print uxm.formatter.get_formatter(options.formatter).format_menu(data)
