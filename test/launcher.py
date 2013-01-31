import sys
import os.path as path
sys.path.insert(0,
    path.abspath(
        path.dirname(path.abspath(__file__)) + '/../usr/lib/uxdgmenu'
    )
)

import uxm.bench as bench

import gtk
from uxm.dialogs.launcher.dialog import LauncherDialog

bench.step('dialog init')
launcher = LauncherDialog()
bench.endstep('dialog init')

gtk.main()

bench.stop()
bench.results()
