from ctypes import *
from ctypes.util import find_library

__all__ = [
    'fadvise',
    'FADV_NORMAL', 'FADV_RANDOM', 'FADV_SEQUENTIAL',
    'FADV_WILLNEED', 'FADV_DONTNEED', 'FADV_NOREUSE'
]

_libc = CDLL(find_library('c'))

_posix_fadvise = _libc.posix_fadvise
_posix_fadvise.argtypes = [c_int, c_int8, c_int8, c_int]
_posix_fadvise.restype = c_int


(
    FADV_NORMAL,
    FADV_RANDOM,
    FADV_SEQUENTIAL,
    FADV_WILLNEED,
    FADV_DONTNEED,
    FADV_NOREUSE
) = range(6)


def fadvise(fd, offset, length, advice):
    return _posix_fadvise(
        c_int(fd),
        c_int8(offset),
        c_int8(length),
        c_int(advice)
    )
