#! /usr/bin/env python

import os, sys, optparse
import uxm.places, uxm.utils

if __name__ == "__main__":
    usage = """%prog window_manager start_directory"""
    parser = optparse.OptionParser(usage=usage)
    options, args = parser.parse_args()
    
    if len(args) < 2:
        parser.print_help()
        sys.exit(1)

    path = os.path.abspath(os.path.expanduser(args[1]))
    menu = uxm.places.PlacesMenu(args[0])
    print menu.parse_path(path)
