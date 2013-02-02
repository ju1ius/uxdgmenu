import os
import locale


def listdir(path, show_files=True, dirs_first=True):
    """
    Returns the content of a directory sorted lexicographically
    """
    items = os.listdir(path)
    isdir = os.path.isdir
    join = os.path.join
    isfile = os.path.isfile
    key_func = locale.strxfrm
    dirs = sorted([d for d in items if isdir(join(path, d))], key=key_func)
    if not show_files:
        return dirs
    files = sorted([f for f in items if isfile(join(path, f))], key=key_func)
    return dirs_first and dirs + files or files + dirs
