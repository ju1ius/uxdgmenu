import os
import subprocess
import time

from xdg.IniFile import IniFile
from fadvise_compat import posix_fadvise, POSIX_FADV_SEQUENTIAL, POSIX_FADV_WILLNEED

APP_DIR = '/usr/share/applications'


def drop_caches():
    subprocess.call("/usr/bin/sudo echo 1 > /proc/sys/vm/drop_caches", shell=True)


def parse():
    for f in os.listdir(APP_DIR):
        if f.endswith('.desktop'):
            path = os.path.join(APP_DIR, f)
            IniFile(path)


def parse_advise():
    #files = []
    for f in os.listdir(APP_DIR):
        if f.endswith('.desktop'):
            path = os.path.join(APP_DIR, f)
            fd = os.open(path, os.O_RDONLY)
            posix_fadvise(fd, 0, 0, POSIX_FADV_SEQUENTIAL | POSIX_FADV_WILLNEED)
            IniFile(path)
            #files.append(path)
    #for f in files:
        #IniFile(path)


if __name__ == "__main__":
    #start = time.time()
    #parse()
    #end = time.time()
    #print "Parse:", end - start

    start = time.time()
    parse_advise()
    end = time.time()
    print "Parse FAdvise:", end - start
