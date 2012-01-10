package="uxdgmenu"
version="0.1"

export prefix=/usr/local
export sysconfdir=/etc

CC=gcc
CFLAGS=-W -Wall -pedantic
LDFLAGS=-linotifytools
EXEC=usr/bin/uxdgmenud
SRC=src/uxdgmenud.c

all: uxdgmenud locale

uxdgmenud:
	${CC} ${SRC} -o ${EXEC} ${LDFLAGS} ${CFLAGS}

locale:
	./scripts/make-locale.sh

.PHONY: clean install uninstall

clean:
	rm -f ${EXEC} 2> /dev/null
	rm -rf usr/share/locale/* 2> /dev/null

install:
	#
	find . -name "*.pyc" | xargs rm -f
	# Modify config paths
	sed -i -e 's#PREFIX = ".*"#PREFIX = "$(prefix)"#' \
		-e 's#SYSCONFDIR = ".*"#SYSCONFDIR = "$(sysconfdir)"#' \
		usr/lib/uxdgmenu/uxm/config.py
	# lib
	install -d $(DESTDIR)$(prefix)/lib/uxdgmenu/uxm/adapters
	install -d $(DESTDIR)$(prefix)/lib/uxdgmenu/uxm/parsers
	install -d $(DESTDIR)$(prefix)/lib/uxdgmenu/uxm/formatters
	install -d $(DESTDIR)$(prefix)/lib/uxdgmenu/uxm/dialogs
	install -m 0755 usr/lib/uxdgmenu/*.py $(DESTDIR)$(prefix)/lib/uxdgmenu
	install -m 0755 usr/lib/uxdgmenu/uxm/*.py $(DESTDIR)$(prefix)/lib/uxdgmenu/uxm
	install -m 0755 usr/lib/uxdgmenu/uxm/adapters/*.py $(DESTDIR)$(prefix)/lib/uxdgmenu/uxm/adapters
	install -m 0755 usr/lib/uxdgmenu/uxm/parsers/*.py $(DESTDIR)$(prefix)/lib/uxdgmenu/uxm/parsers
	install -m 0755 usr/lib/uxdgmenu/uxm/formatters/*.py $(DESTDIR)$(prefix)/lib/uxdgmenu/uxm/formatters
	install -m 0755 usr/lib/uxdgmenu/uxm/dialogs/*.py $(DESTDIR)$(prefix)/lib/uxdgmenu/uxm/dialogs
	install -m 0755 usr/lib/uxdgmenu/uxm/dialogs/*.glade $(DESTDIR)$(prefix)/lib/uxdgmenu/uxm/dialogs
	# bin
	install -d $(DESTDIR)$(prefix)/bin
	install -m 0755 usr/bin/* $(DESTDIR)$(prefix)/bin
	ln -sf -T $(prefix)/lib/uxdgmenu/uxm-daemon.py $(DESTDIR)$(prefix)/bin/uxm-daemon
	ln -sf -T $(prefix)/lib/uxdgmenu/uxm-places.py $(DESTDIR)$(prefix)/bin/uxm-places
	ln -sf -T $(prefix)/lib/uxdgmenu/uxm-menu.py   $(DESTDIR)$(prefix)/bin/uxm-menu
	ln -sf -T $(prefix)/lib/uxdgmenu/uxm-config.py $(DESTDIR)$(prefix)/bin/uxm-config
	# share
	install -d $(DESTDIR)$(prefix)/share/applications
	install -m 0755 usr/share/applications/* $(DESTDIR)$(prefix)/share/applications
	install -d $(DESTDIR)$(prefix)/share/desktop-directories
	install -m 0755 usr/share/desktop-directories/* $(DESTDIR)$(prefix)/share/desktop-directories
	install -d $(DESTDIR)$(prefix)/share/locale
	cp -R usr/share/locale/* $(DESTDIR)$(prefix)/share/locale
	# etc
	install -d $(DESTDIR)$(sysconfdir)/xdg/menus
	install -m 0755 etc/xdg/menus/* $(DESTDIR)$(sysconfdir)/xdg/menus
	install -d $(DESTDIR)$(sysconfdir)/uxdgmenu
	install -m 0755 etc/uxdgmenu/* $(DESTDIR)$(sysconfdir)/uxdgmenu

uninstall:
	-rm -rf $(DESTDIR)$(prefix)/lib/uxdgmenu
	-rm -rf $(DESTDIR)$(prefix)/share/locale/*/LC_MESSAGES/uxdgmenu.mo
	-rm -f $(DESTDIR)$(prefix)/share/desktop-directories/uxm-*.directory
	-rm -rf $(DESTDIR)$(sysconfdir)/uxdgmenu
	-rm -f $(DESTDIR)$(sysconfdir)/xdg/menus/uxm-applications.menu
	-rm -f $(DESTDIR)$(sysconfdir)/xdg/menus/uxm-rootmenu.menu
	-rm -f $(DESTDIR)$(prefix)/bin/uxm-daemon
	-rm -f $(DESTDIR)$(prefix)/bin/uxm-places
	-rm -f $(DESTDIR)$(prefix)/bin/uxm-config
	-rm -f $(DESTDIR)$(prefix)/bin/uxm-menu
	-rm -f $(DESTDIR)$(prefix)/bin/uxdgmenud
