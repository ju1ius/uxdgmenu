#! /usr/bin/env python

import sys
import os.path as path
import logging

sys.path.insert(0, path.abspath(path.dirname(path.abspath(__file__))))

import uxm.bench as bench
import uxm.config
from uxm.dialogs.launcher.dialog import LauncherDialog


if __name__ == "__main__":

    logger = logging.getLogger('uxm-run')
    logger.addHandler(uxm.config.make_log_handler('uxm-run'))
    logger.setLevel(logging.ERROR)

    try:
        bench.step('dialog init')
        launcher = LauncherDialog()
        bench.endstep('dialog init')
        launcher.start()
    except Exception, e:
        logger.exception(e)
        raise

    bench.stop()
    bench.results()
