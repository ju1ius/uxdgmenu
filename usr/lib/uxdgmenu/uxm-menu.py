#! /usr/bin/python

import sys
import logging

import uxm.config as config
from uxm.dialogs.menu import Menu

if __name__ == "__main__":

    logger = logging.getLogger('uxm-editor')
    logger.addHandler(config.make_log_handler('uxm-editor'))
    logger.setLevel(logging.ERROR)

    try:
        menu = Menu()
        menu.main()
    except Exception, e:
        logger.exception(e)
        raise

    sys.exit(0)
