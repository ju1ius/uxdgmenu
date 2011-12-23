#! /usr/bin/env python

from . import uxm.config, uxm.applications
import pprint

if __name__ == "__main__":
    formatter = 'openbox'
    menu_file = 'uxm-applications.menu'
    menu = uxm.applications.ApplicationsMenu(formatter)

    pp = pprint.PrettyPrinter(indent=2, width=80)

    data = menu.parse_menu_file(menu_file)
