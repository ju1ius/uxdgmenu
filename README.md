About
=====

uxdgmenu is an automated XDG Menu system for alternative Linux window managers.
It supports currently Fluxbox, Openbox, Awesome, Blackbox, WindowMaker,
FVWM2, IceWM, Ion3, PekWM, TWM, support can be added to any other through plugins.

uxdgmenu monitors for newly installed/removed applications,
and maintains a submenu, listing and categorizing them like the Gnome/Xfce/Lxde menu.
It can also monitor your gtk bookmarks and recent files,
and comes with a standalone GTK app-launcher and a GUI for configuration.

[Check the wiki](http://github.com/ju1ius/uxdgmenu/wiki)

Install
=======

[Debian packages are provided](https://github.com/ju1ius/udxgmenu/downloads),
but you can also build from source:

Install dependencies:

    sudo aptitude install libglib2.0-dev libglib2.0-0 libinotifytools0 libinotifytools0-dev python-xdg

You should also (but are not forced to) install the following packages:

* python-gtk2: for the GUIs (dialogs, configuration, menu widget...)
* python-gmenu:   makes menu generation 10 times faster...
* python-dbus: for monitoring, mounting & unmounting devices.
You might also need to install the freedesktop.org's ConsoleKit + PolicyKit stack in order to
get mount/unmount permissions as a user.

Clone the git repository if you haven't already

    git clone git://github.com/ju1ius/uxdgmenu.git
    cd uxdgmenu

Build and install

    make && sudo make install prefix=/usr

Next
====

[Check the wiki](http://github.com/ju1ius/uxdgmenu/wiki)

-----------------------------------------------------------------------
uxdgmenu has been inspired by:

* Fedora's xdg-menu
* Shane Lazar's mint-fm2
* Byron Clark's udiskie
* corenominal's crunchbang linux pipemenus for openbox
