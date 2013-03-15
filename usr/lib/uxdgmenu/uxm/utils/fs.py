import sys
import os
import locale


VERSION = sys.version_info


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


if VERSION[0] >= 3 and VERSION[1] >= 3:

    fadvise = os.posix_fadvise
    FADV_NORMAL = os.POSIX_FADV_NORMAL
    FADV_SEQUENTIAL = os.POSIX_FADV_SEQUENTIAL
    FADV_RANDOM = os.POSIX_FADV_RANDOM
    FADV_NOREUSE = os.POSIX_FADV_NOREUSE
    FADV_WILLNEED = os.POSIX_FADV_WILLNEED
    FADV_DONTNEED = os.POSIX_FADV_DONTNEED

else:

    from compat.fadvise import *
