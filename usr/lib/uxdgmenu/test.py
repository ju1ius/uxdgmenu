#! /usr/bin/env python
import os, sys, subprocess, time
import logging
from pprint import pprint as pp

from uxm.dialogs.menu import Menu
menu = Menu()
menu.start()

sys.exit(0)


#from uxm.parsers.applications import Parser
#from uxm.parsers.bookmarks import Parser
#from uxm.parsers.recently_used import Parser
#from uxm.formatters.fluxbox import Formatter

p = Parser()

start_t = time.time()

#data = p.parse_menu_file('uxm-applications.menu')
#data = p.parse_bookmarks()
with open(os.path.expanduser('~/foobar'), 'w') as fp:
    fp.write(f.format_menu(data))

endt_t = time.time()

print ">>> %.8f" % (endt_t - start_t)

#def bench(c):
    #start_t = time.time()
    #for i in xrange(c):
        #output = f.format_menu(data)
    #end_t = time.time()
    #total = end_t - start_t
    #pc = total // c
    #print output
    #print ">>> total=%.8f percall=%.12f" % (total, pc)

#bench(10000)
