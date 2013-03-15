
from ctypes import *
from ctypes.util import find_library

_libc = CDLL(find_library('c'))

_posix_fadvise = _libc.posix_fadvise
_posix_fadvise.argtypes = [c_int, c_int8, c_int8, c_int]
_posix_fadvise.restype = c_int


(
    POSIX_FADV_NORMAL,
    POSIX_FADV_RANDOM,
    POSIX_FADV_SEQUENTIAL,
    POSIX_FADV_WILLNEED,
    POSIX_FADV_DONTNEED,
    POSIX_FADV_NOREUSE
) = range(6)


def posix_fadvise(fd, offset, length, advice):
    return _posix_fadvise(
        c_int(fd),
        c_int8(offset),
        c_int8(length),
        c_int(advice)
    )
