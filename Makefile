package="uxdgmenu"
version="0.2"

export prefix=/usr/local
export sysconfdir=/etc

CC      := gcc
CFLAGS  := `pkg-config --cflags glib-2.0 gthread-2.0 gio-2.0` -W -Wall -pedantic
LDFLAGS := `pkg-config --libs glib-2.0 gthread-2.0 gio-2.0` -linotifytools
EXEC    := usr/bin/uxdgmenud
SRC     := src/uxdgmenud.c

all: uxdgmenud locale

uxdgmenud:
	# add -g -O0 flags for debugging,
	# along with "ulimit -c unlimited" in the debugging console session
	$(CC) $(SRC) -o $(EXEC) $(LDFLAGS) $(CFLAGS) -g -O0

locale:
	./scripts/make-locale.sh

.PHONY: clean install uninstall

clean:
	rm -f ${EXEC} 2> /dev/null
	rm -rf usr/share/locale/* 2> /dev/null

install:
	# remove pyc
	find . -name "*.pyc" | xargs rm -f
	# Modify config paths
	sed -i -e 's#PREFIX = ".*"#PREFIX = "$(prefix)"#' \
		-e 's#SYSCONFDIR = ".*"#SYSCONFDIR = "$(sysconfdir)"#' \
		usr/lib/uxdgmenu/uxm/config.py
	# install dirs under prefix/lib
	find usr/lib/uxdgmenu -type d \
		| sed "s#.*/uxdgmenu/\(.*\)#$(DESTDIR)$(prefix)/lib/uxdgmenu/\1#" \
		| xargs install -d
	# install files under prefix/lib
	find usr/lib/uxdgmenu -type f -name "*.py" -or -name "*.glade" | while read file; do \
		dir=`dirname "$$file"`; \
		dest=`echo "$$dir" | sed "s#\(.*\)usr/lib/uxdgmenu#$(DESTDIR)$(prefix)/lib/uxdgmenu#"`; \
		install -m 0755 "$$file" "$$dest"; \
	done
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
