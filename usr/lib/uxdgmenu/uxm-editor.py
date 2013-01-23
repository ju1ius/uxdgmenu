#! /usr/bin/env python

import sys, os
__DIR__ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, __DIR__)

#from gi.repository import Gtk
import gtk

import uxm.config as config
#import uxm.editor.maindialog as editor
import uxm.editor.maindialog_gtk2 as editor

options_parser = config.OptionParser()
options, args = options_parser.parse_args()

if len(args) < 1:
    prefs = config.preferences()
    menu_file = prefs.get('Applications', 'menu_file')
    if not menu_file:
        menu_file = 'uxm-applications.menu'
    args =  [menu_file]

dialog = editor.MenuEditorDialog(['uxm-applications.menu'])


gtk.main()
