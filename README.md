About
=====

uxdgmenu is an automated XDG Menu system for alternative Linux window managers.
It supports currently fluxbox, openbox, awesome, and is easily extensible.

uxdgmenu monitors for newly installed/removed applications,
and maintains a submenu, listing and categorizing them like the Gnome/Xfce/Lxde menu.
It can also monitor your gtk bookmarks and recent files,
and comes with a standalone GTK app-launcher and a GUI for configuration.

uxdgmenu is written in C and Python and only requires the following packages:

* libinotifytools0
* python-xdg

Install
=======

Install dependencies:

    sudo aptitude install libinotifytools0 libinotifytools0-dev python-xdg

You can also optionally install the following packages:

* python-gtk2:    enables uxdgmenu to use your current GTK icon theme and GUI dialogs
* python-gmenu:   makes menu generation 10 times faster...
* python-gobject: enables the recently used files menu to display item icons
                  according to their mime type.

Clone the git repository if you haven't already

    git clone git://github.com/ju1ius/uxdgmenu.git
    cd uxdgmenu

Build and install

    make && sudo make install

Next
====

[Check the wiki](http://github.com/ju1ius/uxdgmenu/wiki)

-----------------------------------------------------------------------
uxdgmenu is heavily inspired by:

* [xdg-menu](http://cvs.fedoraproject.org/viewvc/devel/openbox/xdg-menu)
