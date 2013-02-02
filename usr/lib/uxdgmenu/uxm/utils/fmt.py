
__filesize_fmt = [
    (1000 ** 5, 'PB'),
    (1000 ** 4, 'TB'),
    (1000 ** 3, 'GB'),
    (1000 ** 2, 'MB'),
    (1000 ** 1, 'KB'),
    (1000 ** 0, 'B')
]


def round_base(x, base=8):
    """Returns the nearest integer which is a multiple of base"""
    return int(base * round(float(x)/base))


def filesize(size):
    for factor, suffix in __filesize_fmt:
        if size >= factor:
            break
    amount = int(size/factor)
    return "%s %s" % (str(amount), suffix)
