import os, re, pwd, shlex, subprocess
import xdg.BaseDirectory

def round_base(x, base=8):
    """Returns the nearest integer which is a multiple of base"""
    return int(base * round(float(x)/base))

EXE_REGEX = re.compile(r' [^ ]*%[fFuUdDnNickvm]')

def clean_exec(cmd):
    """Cleans commands found in Desktop entries"""
    return EXE_REGEX.sub('', cmd)

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

def guess_open_cmd():
    """Tries to guess the command to open files
    with their associated application.
    If it fails, defaults to xdg-open"""
    for cmd in ['exo-open', 'kde-open','gnome-open']:
        if which(cmd):
            return cmd
    return 'xdg-open'

def guess_file_manager():
    """Tries to get the default application
    for the inode/directory mime type,
    which should be the default file manager...
    If it fails, we try a list of known filemanagers,
    or default to xdg-open"""
    desktop_file_name = find_desktop_file_by_mime_type('inode/directory')
    if desktop_file_name:
        desktop_file = find_desktop_file(desktop_file_name)
        if desktop_file:
            return desktop_file_get_exec(desktop_file)
    for fm in ['thunar', 'pcmanfm', 'nautilus', 'dolphin']:
        if which(fm):
            return fm
    return 'xdg-open'

def find_desktop_file(filename):
    if os.path.isabs(filename):
        return filename
    for d in xdg.BaseDirectory.load_data_paths('applications'):
        filepath = os.path.join(d, filename)
        if os.path.isfile(filepath):
            return filepath

def find_desktop_file_by_mime_type(mime_type):
    for d in xdg.BaseDirectory.load_data_paths('applications'):
        filename = os.path.join(d, 'mimeapps.list')
        if not os.path.isfile(filename):
            filename = os.path.join(d, 'defaults.list')
            if not os.path.isfile(filename):
                break
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

def detect_de():
    if os.getenv('KDE_FULL_SESSION'):
        return 'kde'
    elif check_gnome():
        return 'gnome'
    elif check_xfce():
        return 'xfce'
    else:
        return os.getenv('DESKTOP_SESSION', '').lower()

def check_gnome():
    if os.getenv('GNOME_DESKTOP_SESSION_ID'):
        return True
    args = shlex.split(
        "dbus-send --print-reply --dest=org.freedesktop.DBus /org/freedesktop/DBus org.freedesktop.DBus.GetNameOwner string:org.gnome.SessionManager > /dev/null 2>&1"        
    )
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    r = p.communicate()
    if not r[1]:
        return True

def check_xfce():
    args = shlex.split("xprop -root _DT_SAVE_MODE")
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    r = p.communicate()
    if r[1]:
        return False
    if ' = "xfce4"' in r[0]:
        return True



def pgrep(pattern, **kwargs):
    return_name = False
    exact_match = False
    invert_match = False
    check_user = False
    check_cmdline = False
    if 'name' in kwargs:
        return_name = kwargs['name'] if kwargs['name'] is True else False
    if 'exact' in kwargs:
        exact_match = kwargs['exact'] if kwargs['exact'] is True else False
    if 'invert' in kwargs:
        invert_match = kwargs['invert'] if kwargs['invert'] is True else False
    if 'cmdline' in kwargs:
        check_cmdline = kwargs['cmdline'] if kwargs['cmdline'] is True else False
    if 'user' in kwargs:
        uid = pwd.getpwnam(kwargs['user']).pw_uid
        check_user = True
    if not exact_match:
        pattern = re.compile(pattern, re.I)
    matches = []
    append = matches.append

    pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
    for pid in pids:
        pid_dir = os.path.join('/proc', pid)
        pid_matches = False
        ret = [int(pid), None]
        if check_cmdline:
            cmdline_file = os.path.join(pid_dir, 'cmdline')
            if os.path.exists(cmdline_file):
                with open(cmdline_file, 'r') as f:
                    cmdline = f.read().strip()
                    if _pgrep_return_if_matches(pattern, cmdline, exact_match, invert_match):
                        pid_matches = True
        status_file = os.path.join(pid_dir, 'status')
        if os.path.exists(status_file):
            with open(status_file, 'r') as f:
                lines = f.readlines()
                if check_user:
                    data = lines[6].partition(':')[2].split()[0]
                    if int(data) != uid:
                        continue
                if return_name or not check_cmdline:
                    name = lines[0].partition(':')[2].strip()
                    if _pgrep_return_if_matches(pattern, name, exact_match, invert_match):
                        pid_matches = True
                        ret[1] = name
        if pid_matches:
            if return_name:
                append(tuple(ret))
            else:
                append(ret[0])
    return matches

def _pgrep_return_if_matches(pattern, subject, exact_match, invert_match):
    if exact_match:
        if invert_match:
            if pattern != subject:
                return True
        else:
            if pattern == subject:
                return True
    else:
        if invert_match:
            if not pattern.search(subject):
                return True
        else:
            if pattern.search(subject):
                return True
    return False
