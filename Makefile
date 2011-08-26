package="uxdgmenu"
version="0.1"

export prefix=/usr/local
export sysconfdir=/etc

CC=gcc
CFLAGS=-W -Wall -pedantic
LDFLAGS=-linotifytools
EXEC=usr/bin/uxdgmenud
SRC=src/uxdgmenud.c

uxm-watch:
	${CC} ${SRC} -o ${EXEC} ${LDFLAGS} ${CFLAGS}

.PHONY: clean install uninstall

clean:
	rm ${EXEC}

install:
	install -d ${prefix}/bin
	install -m 0755 usr/bin/* ${prefix}/bin
	install -d ${prefix}/lib/uxdgmenu/uxdgmenu
	install -m 0755 usr/lib/uxdgmenu/uxdgmenu/* ${prefix}/lib/uxdgmenu/uxdgmenu
	install -m 0755 usr/lib/uxdgmenu/uxm-daemon.py ${prefix}/lib/uxdgmenu
	ln -sf -T ${prefix}/lib/uxdgmenu/uxm-daemon.py ${prefix}/bin/uxm-daemon
	install -d ${prefix}/share/desktop-directories
	install -m 0755 usr/share/desktop-directories/* ${prefix}/share/desktop-directories
	install -d ${sysconfdir}/xdg/menus
	install -m 0755 etc/xdg/menus/* ${sysconfdir}/xdg/menus
	install -d ${sysconfdir}/uxdgmenu
	install -m 0755 etc/uxdgmenu/* ${sysconfdir}/uxdgmenu

uninstall:
	-rm -rf ${prefix}/lib/uxdgmenu
	-rm -f ${prefix}/share/desktop-directories/uxm-*.directory
	-rm -rf ${sysconfdir}/uxdgmenu
	-rm -f ${sysconfdir}/xdg/menus/uxm-applications.menu
	-rm -f ${prefix}/bin/uxm-daemon
	-rm -f ${prefix}/bin/uxdgmenud
