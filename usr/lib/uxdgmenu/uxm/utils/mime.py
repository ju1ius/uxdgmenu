import os
import stat
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


def guess(filepath):
    data, is_file = None, False
    try:
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
    except:
        pass
    if is_file:
        try:
            with open(filepath, 'rb') as fp:
                data = fp.read(MIME_MAGIC_MAX_BUF_SIZE)
        except:
            pass
        # Removed in favor of gio, this was way too sloooow !
        #mime_type = xdg.Mime.get_type(filepath)
        mime_type = gio.content_type_guess(filepath, data, False)
    return mime_type


def get_apps_for_type(mimetype):
    return gio.app_info_get_all_for_type(mimetype)


def get_default_app(mimetype):
    return gio.app_info_get_default_for_type(mimetype)
