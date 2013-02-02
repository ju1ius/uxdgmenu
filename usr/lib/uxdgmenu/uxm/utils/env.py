import os
import pwd
import shlex
import subprocess

from . import mime


def is_executable(fpath):
    return os.path.exists(fpath) and os.access(fpath, os.X_OK)


def which(program):
    """Check for external modules or programs"""
    fpath, fname = os.path.split(program)
    if fpath:
        if is_executable(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_executable(exe_file):
                return exe_file
    return None


def list_real_users():
    """Finds real users by reading /etc/pswd
        returns a Tuple containing the username and home dir"""
    for p in pwd.getpwall():
        if p[5].startswith('/home') and p[6] != "/bin/false":
            yield (p[0], p[5])


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
    args = shlex.split("""dbus-send --print-reply --dest=org.freedesktop.DBus \
        /org/freedesktop/DBus org.freedesktop.DBus.GetNameOwner \
        string:org.gnome.SessionManager > /dev/null 2>&1""")
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


def guess_open_cmd():
    """Tries to guess the command to open files
    with their associated application.
    If it fails, defaults to xdg-open"""
    for cmd in ['exo-open', 'kde-open', 'gnome-open']:
        if which(cmd):
            return cmd
    return 'xdg-open'


def guess_file_manager():
    """Tries to get the default application
    for the inode/directory mime type,
    which should be the default file manager...
    If it fails, we try a list of known filemanagers,
    or default to xdg-open"""
    app_info = mime.get_default_app('inode/directory')
    if app_info:
        return app_info.get_commandline()
    for fm in ['thunar', 'pcmanfm', 'nautilus', 'dolphin']:
        if which(fm):
            return fm
    return 'xdg-open'


def guess_terminal():
    for term in ('x-terminal-emulator', 'terminator', 'lxterminal',
                    'xfce4-terminal', 'gnome-terminal', 'urxvt', 'xterm'):
        if which(term):
            return term
