import os
import multiprocessing
import time

from xdg.Exceptions import ParsingError
import xdg.Menu
from xdg.Menu import MenuEntry


def parse_desktop_file(item):
    path, dir, prefix = item
    try:
        menuentry = MenuEntry(path, dir, prefix)
    except ParsingError:
        return
    return menuentry, dir


class MenuEntryCache:
    "Class to cache Desktop Entries"
    def __init__(self):
        self.cacheEntries = {}
        self.cacheEntries['legacy'] = []
        self.cache = {}

    def addMenuEntries(self, dirs, prefix="", legacy=False):
        for dir in dirs:
            if not dir in self.cacheEntries:
                self.cacheEntries[dir] = []
                self.addFiles(dir, "", prefix, legacy)

    def __addFiles(self, dir, subdir, prefix, legacy):
        for item in os.listdir(os.path.join(dir, subdir)):
            if os.path.splitext(item)[1] == ".desktop":
                try:
                    menuentry = MenuEntry(os.path.join(subdir, item), dir, prefix)
                except ParsingError:
                    continue

                self.cacheEntries[dir].append(menuentry)
                if legacy:
                    self.cacheEntries['legacy'].append(menuentry)
            elif os.path.isdir(os.path.join(dir, subdir, item)) and not legacy:
                self.__addFiles(dir, os.path.join(subdir, item), prefix, legacy)

    def addFiles(self, dir, subdir, prefix, legacy):
        files = [f for f in self.iter_appdirs(dir, subdir, prefix, legacy)]
        pool = multiprocessing.Pool()
        entries = pool.map(parse_desktop_file, files, 32)
        for menuentry, dir in entries:
            self.cacheEntries[dir].append(menuentry)
            if legacy:
                self.cacheEntries['legacy'].append(menuentry)

    def iter_appdirs(self, dir, subdir, prefix, legacy):
        for item in os.listdir(os.path.join(dir, subdir)):
            if item.endswith(".desktop"):
                yield os.path.join(subdir, item), dir, prefix
            elif os.path.isdir(os.path.join(dir, subdir, item)) and legacy is False:
                for p in self.iter_appdirs(dir, os.path.join(subdir, item), prefix, legacy):
                    yield p

    def getMenuEntries(self, dirs, legacy=True):
        list = []
        ids = []
        # handle legacy items
        appdirs = dirs[:]
        if legacy:
            appdirs.append("legacy")
        # cache the results again
        key = "".join(appdirs)
        try:
            return self.cache[key]
        except KeyError:
            pass
        for dir in appdirs:
            for menuentry in self.cacheEntries[dir]:
                try:
                    if menuentry.DesktopFileID not in ids:
                        ids.append(menuentry.DesktopFileID)
                        list.append(menuentry)
                    elif menuentry.getType() == "System":
                    # FIXME: This is only 99% correct, but still...
                        i = list.index(menuentry)
                        e = list[i]
                        if e.getType() == "User":
                            e.Original = menuentry
                except UnicodeDecodeError:
                    continue
        self.cache[key] = list
        return list


start = time.time()
xdg.Menu.parse('kde4-applications.menu')
end = time.time()
print "Sync: ", end - start

xdg.Menu.MenuEntryCache = MenuEntryCache

start = time.time()
xdg.Menu.parse('kde4-applications.menu')
end = time.time()
print "Multiproc: ", end - start
