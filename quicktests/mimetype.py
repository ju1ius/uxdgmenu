import os
import time
import stat
import multiprocessing
import gio
import xdg.Mime

xdg.Mime.update_cache()
MIME_MAGIC_MAX_BUF_SIZE = xdg.Mime.magic.maxlen

# Some well-known types
INODE_BLOCK = str(xdg.Mime.inode_block)
INODE_CHAR = str(xdg.Mime.inode_char)
INODE_DIR = str(xdg.Mime.inode_dir)
INODE_FIFO = str(xdg.Mime.inode_fifo)
INODE_SOCKET = str(xdg.Mime.inode_socket)
INODE_SYMLINK = str(xdg.Mime.inode_symlink)
INODE_DOOR = str(xdg.Mime.inode_door)
APP_EXE = str(xdg.Mime.app_exe)
APP_OCTET_STREAM = 'application/octet-stream'


def guess(filepath, use_contents=True):
    data, is_file = None, False
    mime_type = APP_OCTET_STREAM
    #try:
    st = os.stat(filepath)
    st_mode = st.st_mode
    if stat.S_ISDIR(st_mode):
        mime_type = INODE_DIR
    elif stat.S_ISCHR(st_mode):
        mime_type = INODE_CHAR
    elif stat.S_ISBLK(st_mode):
        mime_type = INODE_BLOCK
    elif stat.S_ISFIFO(st_mode):
        mime_type = INODE_FIFO
    elif stat.S_ISLNK(st_mode):
        mime_type = INODE_SYMLINK
    elif stat.S_ISSOCK(st_mode):
        mime_type = INODE_SOCKET
    elif stat.S_ISREG(st_mode):
        is_file = True
    #except:
        #pass
    if is_file:
        if use_contents:
            try:
                with open(filepath, 'rb') as fp:
                    data = fp.read(MIME_MAGIC_MAX_BUF_SIZE)
            except:
                pass
        # Removed in favor of gio, this was way too sloooow !
        #mime_type = xdg.Mime.get_type(filepath)
        mime_type = gio.content_type_guess(filepath, data, False)
    return mime_type


def list_path():
    for d in os.environ['PATH'].split(':'):
        for f in os.listdir(d):
            fp = os.path.join(d, f)
            if not os.path.isfile(fp):
                continue
            yield fp


def do_guess(fp):
    mt = guess(fp)
    return fp, mt


def get_mimetypes_async():
    pool = multiprocessing.Pool(processes=4)
    res = []
    for app in list_path():
        pool.apply_async(do_guess, (app,), {}, res.append)
    pool.close()
    pool.join()
    return res


def get_mimetypes_async2():
    pool = multiprocessing.Pool(processes=4)
    paths = [a for a in list_path()]
    return pool.map(do_guess, paths, 64)


def get_mimetypes_async3():
    pool = multiprocessing.Pool(processes=4)
    paths = [a for a in list_path()]
    return pool.map_async(do_guess, paths, 64)


def get_mimetypes():
    res = []
    for app in list_path():
        mt = guess(app)
        res.append((app, mt))
    return res


start = time.time()
r1 = get_mimetypes()
end = time.time() - start
print "Sync: %s" % end


start = time.time()
r2 = get_mimetypes_async()
end = time.time() - start
print "Async: %s" % end


start = time.time()
r3 = get_mimetypes_async2()
end = time.time() - start
print "Async 2: %s" % end

assert r1 == r2
assert r1 == r3
