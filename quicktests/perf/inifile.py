import re
import io
import os
import time


COMMENT_RX = re.compile(r'(^\s*#|^\s*$)')
GROUP_RX = re.compile(r'^\[([^\]]+)\]$')
KEY_RX = re.compile(r'^([^=]+)\s*=\s*(.*)$')


def parse(self, filename, headers=None):
    content = self.content
    fd = io.open(filename, 'r', encoding='utf-8', errors='replace')
    currentGroup = None
    for line in fd:
        line = line.strip()
        if not line or line[0] == '#':
            continue
        elif line[0] == '[':
            grp = line.strip('[]')
            if grp:
                currentGroup = grp
                content[currentGroup] = {}
        else:
            m = KEY_RX.match(line)
            if m:
                key = m.group(1)
                value = m.group(2)
                content[currentGroup][key] = value
    fd.close()
    self.filename = filename
    self.tainted = False
    if headers:
        for header in headers:
            if headers in content:
                self.defaultGroup = header
                break


from xdg.IniFile import IniFile

path = '/usr/share/applications'
apps = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.desktop')]
print "Test parsing %s desktop files" % len(apps)

start = time.time()
for app in apps:
    res = IniFile(app)
end = time.time()
print "xdg.IniFile:", end - start

IniFile.parse = parse

start = time.time()
for app in apps:
    res = IniFile(app)
end = time.time()
print "Patched xdg.IniFile:", end - start


from gi.repository import GLib

start = time.time()
for app in apps:
    kf = GLib.KeyFile()
    res = kf.load_from_file(app, 0)
end = time.time()
print "GLib.KeyFile:", end - start
