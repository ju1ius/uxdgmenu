#! /usr/bin/env python

import sys
import os
import logging

__DIR__ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, __DIR__)

#from gi.repository import Gtk
import gtk

import uxm.config as config
import uxm.dialogs.editor.maindialog as editor


if __name__ == "__main__":

    options_parser = config.OptionParser()
    options, args = options_parser.parse_args()

    if len(args) < 1:
        prefs = config.preferences()
        menu_file = prefs.get('Applications', 'menu_file')
        if not menu_file:
            menu_file = 'uxm-applications.menu'

    logger = logging.getLogger('uxm-editor')
    logger.addHandler(config.make_log_handler('uxm-editor'))
    logger.setLevel(logging.ERROR)

    try:
        dialog = editor.MenuEditorDialog(menu_file)
        gtk.main()
    except Exception, e:
        logger.exception(e)
        raise
