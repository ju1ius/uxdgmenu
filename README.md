About
=====

uxdgmenu is an automated XDG Menu system for alternative Linux window managers.
It currently supports fluxbox, openbox, blackbox, windowmaker, twm, fvwm2, ion3, awesome, icewm, and pekwm.

uxdgmenu monitors for newly installed/removed applications,
and maintains a submenu, listing and categorizing them like the Gnome/Xfce/Lxde menu.

uxdgmenu is written in C and Python and only requires the following packages:

* libinotifytools0
* python-xdg

Install
=======

Install dependencies (assuming you already have fluxbox bash and python...):

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
