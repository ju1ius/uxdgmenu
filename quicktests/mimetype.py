import os
import time
import stat
import multiprocessing
import threading
import gobject
import gio
import xdg.Mime

xdg.Mime.update_cache()
MIME_MAGIC_MAX_BUF_SIZE = xdg.Mime.magic.maxlen
print MIME_MAGIC_MAX_BUF_SIZE

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


class Queueable(object):

    @property
    def queue(self):
        return self._queue

    @queue.setter
    def queue(self, queue):
        self._queue = queue


class Listener(Queueable, gobject.GObject):
    __gsignals__ = {
        'updated': (
            gobject.SIGNAL_RUN_LAST,
            gobject.TYPE_NONE,
            (gobject.TYPE_PYOBJECT,)
        ),
        'error': (
            gobject.SIGNAL_RUN_LAST,
            gobject.TYPE_NONE,
            (gobject.TYPE_STRING,)
        ),
        'finished': (
            gobject.SIGNAL_RUN_LAST,
            gobject.TYPE_NONE,
            ()
        )
    }

    def __init__(self, queue, max_results):
        gobject.GObject.__init__(self)
        self.queue = queue
        self.max_results = max_results
        self.num_results = 0
        self.stopevent = threading.Event()

    def run(self):
        if self.queue is None:
            raise RuntimeError('Listener must be associated with a Queue')
        while not self.stopevent.isSet():
            # Listen for results on the queue and process them accordingly
            data = self.queue.get()
            # Check if finished
            self.num_results += 1
            if self.num_results == self.max_results:
                self.emit("finished")
                self.stop()
            elif data[0] == "error":
                self.emit('error', data[1])
                self.stop()
            else:
                self.emit('updated', data)

    def stop(self):
        self.stopevent.set()


def do_guess(path, queue):
    mimetype = guess(path)
    queue.put((path, mimetype))


def get_mimetypes_async():
    manager = multiprocessing.Manager()
    queue = manager.Queue()
    pool = multiprocessing.Pool()
    num_apps = 0
    for app in list_path():
        num_apps += 1
        pool.apply_async(do_guess, (app, queue))
    pool.close()
    listener = Listener(queue, num_apps)
    listener.connect('updated', on_result)
    # Starting Listener
    thread = threading.Thread(target=listener.run, args=())
    thread.start()
    thread.join()


def on_result(self, result):
    return
    print result


def get_mimetypes_sync():
    for app in list_path():
        mimetype = guess(app)


#start = time.time()
#r1 = get_mimetypes_sync()
#end = time.time() - start
#print "Sync: %s" % end

start = time.time()
r1 = get_mimetypes_async()
end = time.time() - start
print "Async: %s" % end
