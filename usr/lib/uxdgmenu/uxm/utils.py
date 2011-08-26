import os, re, pwd, subprocess
import xdg.BaseDirectory
from . import config

def sort_ci(inlist, minisort=True):
    """
    Case insensitive sorting)
    If minisort=False, sort_ci will not sort sets of entries
    for which entry1.lower() == entry2.lower()
    i.e. sort_ci(['fish', 'FISH', 'fIsh'], False)
    returns ['fish', 'FISH', 'fIsh']
    instead of ['FISH', 'fIsh', 'fish']
    """
    sortlist = []
    newlist = []
    sortdict = {}
    for entry in inlist:
        try:
            lentry = entry.lower()
        except AttributeError:
            sortlist.append(lentry)
        else:
            try:
                sortdict[lentry].append(entry)
            except KeyError:
                sortdict[lentry] = [entry]
                sortlist.append(lentry)

    sortlist.sort()
    for entry in sortlist:
        try:
            thislist = sortdict[entry]
            if minisort: thislist.sort()
            newlist = newlist + thislist
        except KeyError:
            newlist.append(entry)
    return newlist

def sorted_listdir(path, show_files=True):
    """
    Returns the content of a directory by showing directories first
    and then files by ordering the names alphabetically
    """
    items = os.listdir(path)
    files = sort_ci(d for d in items if os.path.isdir(os.path.join(path, d)))
    if show_files:
        files.extend(sort_ci(f for f in items if os.path.isfile(os.path.join(path, f))))
    return files


def list_real_users():
    """Finds real users by reading /etc/pswd
        returns a Tuple containing the username and home dir"""
    for p in pwd.getpwall():
        if p[5].startswith('/home') and p[6] != "/bin/false":
            yield (p[0], p[5])

def which(program):
    """Check for external modules or programs"""
    def is_exe(fpath):
        return os.path.exists(fpath) and os.access(fpath, os.X_OK)
    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return None

def zenity_progress(cmd, opts_str=' '):
    """Displays a zenity progress bar for the given command"""
    subprocess.call(
        "(%s%s%s) | zenity --progress --pulsate --auto-close" % (
            config.APP_DAEMON, opts_str, cmd
        ),
        shell=True
    )

def get_options_for_progress(options):
    # Remember to leave spaces around options !!!
    opt_list = []
    if options.window_manager:
        opt_list.append('-w %s' % options.window_manager)
    if options.all:
         opt_list.append('-a')
         return ' '.join(opt_list)
    if options.with_bookmarks:
        opt_list.append('-b')
    if options.with_recently_used:
        opt_str.append('-r ')
    return ' '.join(opt_list)

def get_default_filemanager():
    """Tries to get the default application for the inode/directory mime type,
    which should be the default file manager..."""
    desktop_file_name = find_desktop_file_by_mime_type('inode/directory')
    if desktop_file_name:
        desktop_file = find_desktop_file(desktop_file_name)
        if desktop_file:
            return desktop_file_get_exec(desktop_file)

def find_desktop_file(filename):
    if os.path.isabs(filename):
        return filename
    for d in xdg.BaseDirectory.load_data_paths('applications'):
        filepath = os.path.join(d, filename)
        if os.path.isfile(filepath):
            return filepath

def find_desktop_file_by_mime_type(mime_type):
    mime_associations = [
        os.path.expanduser('~/.local/share/applications/mimeapps.list'),        
        os.path.expanduser('~/.local/share/applications/defaults.list'),        
        os.path.expanduser('/usr/share/applications/defaults.list'),        
    ]
    for filename in mime_associations:
        r = find_mime_association(filename, mime_type)
        if r:
            return r

def find_mime_association(filename, mime_type):
    with open(filename, 'r') as f:
        l = f.readline()
        while l:
            if l.startswith(mime_type):
                return l.strip().split('=')[-1].split(';')[0]
            l = f.readline()

def desktop_file_get_exec(filename):
    with open(filename, 'r') as f:
        l = f.readline()
        while l:
            if l.startswith('Exec'):
                fm = l.strip().split('=')[1]
                return re.sub(r'%[a-zA-Z]+', '', fm)
            l = f.readline()
