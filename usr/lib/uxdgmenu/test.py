#! /usr/bin/env python
import os, subprocess, time

#import uxm.applications, uxm.formatters.openbox as formatter
import uxm.applications, uxm.formatters.awesome as formatter
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
