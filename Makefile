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
	rm ${EXEC}
	rm -rf usr/share/locale/* 2> /dev/null

install:
	# Modify config paths
	sed -i -e 's/PREFIX = ".*"/PREFIX = "${prefix}"/' \
		-e 's/SYSCONFDIR = ".*"/SYSCONFDIR = "${sysconfdir}"/' \
		usr/lib/uxdgmenu/uxm/config.py
	# lib
	install -d ${prefix}/lib/uxdgmenu/uxm/adapters
	install -d ${prefix}/lib/uxdgmenu/uxm/formatters
	install -m 0755 usr/lib/uxdgmenu/*.py ${prefix}/lib/uxdgmenu
	install -m 0755 usr/lib/uxdgmenu/uxm/*.py ${prefix}/lib/uxdgmenu/uxm
	install -m 0755 usr/lib/uxdgmenu/uxm/adapters/*.py ${prefix}/lib/uxdgmenu/uxm/adapters
	install -m 0755 usr/lib/uxdgmenu/uxm/formatters/*.py ${prefix}/lib/uxdgmenu/uxm/formatters
	# bin
	install -d ${prefix}/bin
	install -m 0755 usr/bin/* ${prefix}/bin
	ln -sf -T ${prefix}/lib/uxdgmenu/uxm-daemon.py ${prefix}/bin/uxm-daemon
	ln -sf -T ${prefix}/lib/uxdgmenu/uxm-places.py ${prefix}/bin/uxm-places
	# share
	install -d ${prefix}/share/applications
	install -m 0755 usr/share/applications/* ${prefix}/share/applications
	install -d ${prefix}/share/desktop-directories
	install -m 0755 usr/share/desktop-directories/* ${prefix}/share/desktop-directories
	install -d ${prefix}/share/locale
	cp -R usr/share/locale/* ${prefix}/share/locale
	# etc
	install -d ${sysconfdir}/xdg/menus
	install -m 0755 etc/xdg/menus/* ${sysconfdir}/xdg/menus
	install -d ${sysconfdir}/uxdgmenu
	install -m 0755 etc/uxdgmenu/* ${sysconfdir}/uxdgmenu

uninstall:
	-rm -rf ${prefix}/lib/uxdgmenu
	-rm -rf ${prefix}/share/locale/*/LC_MESSAGES/uxdgmenu.mo
	-rm -f ${prefix}/share/desktop-directories/uxm-*.directory
	-rm -rf ${sysconfdir}/uxdgmenu
	-rm -f ${sysconfdir}/xdg/menus/uxm-applications.menu
	-rm -f ${sysconfdir}/xdg/menus/uxm-rootmenu.menu
	-rm -f ${prefix}/bin/uxm-daemon
	-rm -f ${prefix}/bin/uxm-places
	-rm -f ${prefix}/bin/uxdgmenud
