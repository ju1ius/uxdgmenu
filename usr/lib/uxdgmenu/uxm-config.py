#! /usr/bin/python

import logging

import uxm.config
import uxm.dialogs.config


if __name__ == "__main__":

    logger = logging.getLogger('uxm-config')
    logger.addHandler(uxm.config.make_log_handler('uxm-config'))
    logger.setLevel(logging.ERROR)
    try:
        editor = uxm.dialogs.config.ConfigEditor()
        editor.main()
    except Exception, e:
        logger.exception(e)
        raise
