#! /usr/bin/env python
import os, subprocess, time
from pprint import pprint as pp

#import uxm.applications, uxm.formatters.openbox3 as formatter
import uxm.applications, uxm.formatters.awesome2 as formatter
menu = uxm.applications.ApplicationsMenu()
data = menu.parse_menu_file('uxm-applications.menu')
f = formatter.Formatter()

def bench(c):
    start_t = time.time()
    for i in xrange(c):
        output = f.format_menu(data)
    end_t = time.time()
    total = end_t - start_t
    pc = total // c
    print output
    print ">>> total=%.8f percall=%.12f" % (total, pc)

bench(10000)

#pp(data)
#pprint.pprint(  )
#print output


#import uxm.rootmenu
#menu = uxm.rootmenu.RootMenu('awesome')
#print menu.parse_menu_file('uxm-rootmenu.menu')
#import uxm.bookmarks
#menu = uxm.bookmarks.BookmarksMenu('openbox')
#print menu.parse_bookmarks()
