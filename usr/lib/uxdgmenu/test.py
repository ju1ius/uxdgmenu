#! /usr/bin/env python
import os, sys, subprocess, time
import logging

logging.basicConfig(level=logging.DEBUG)

from yapsy.PluginManager import PluginManager
import uxm.formatters.base

plugins_dirs = [
    os.path.join(os.path.dirname(__file__), "uxm","plugins")       
]
# Create plugin manager
manager = PluginManager(
    categories_filter={ "Formatters": uxm.formatters.base.Formatter },
    directories_list=plugins_dirs,
    plugin_info_ext="ini"
)
# Load plugins
manager.collectPlugins()
plugin = manager.getPluginByName('Fluxbox Formatter', 'Formatters')
#for plugin in manager.getAllPlugins():
    #print dir(plugin.plugin_object)

#sys.exit(0)

from uxm.parsers.applications import Parser
#from uxm.parsers.bookmarks import Parser
#from uxm.parsers.recently_used import Parser
#from uxm.formatters.fluxbox import Formatter

p = Parser()
f = plugin.plugin_object

start_t = time.time()

data = p.parse_menu_file('uxm-applications.menu')
#data = p.parse_bookmarks()
print f.format_menu(data)

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
