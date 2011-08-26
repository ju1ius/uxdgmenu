#! /usr/bin/env python
import os, subprocess

#USER = os.environ['USER']
#if USER == 'root':
    #print os.environ['SUDO_USER']
#print os.environ['USER']
#print os.path.expanduser('~')

#ret = subprocess.call(['pkill', 'foo'])
#print ret
#import uxm.base
#menu = uxm.base.Menu('foobar')

import uxm.applications
menu = uxm.applications.ApplicationsMenu('awesome')
print menu.parse_menu_file('uxm-applications.menu')

#import uxm.rootmenu
#menu = uxm.rootmenu.RootMenu('awesome')
#print menu.parse_menu_file('uxm-rootmenu.menu')
#import uxm.bookmarks
#menu = uxm.bookmarks.BookmarksMenu('openbox')
#print menu.parse_bookmarks()
