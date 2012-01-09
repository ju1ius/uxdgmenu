import multiprocessing, threading, Queue

import pygtk
pygtk.require('2.0')
import gtk
import gobject

import uxm.dialogs.error


class Queueable(object):

    @property
    def queue(self):
        return self._queue
    @queue.setter
    def queue(self, queue):
        self._queue = queue


class Listener(Queueable, gobject.GObject):
    __gsignals__ = {
        'updated' : (
            gobject.SIGNAL_RUN_LAST,
            gobject.TYPE_NONE,
            (gobject.TYPE_FLOAT, gobject.TYPE_STRING)
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

    def __init__(self, queue=None):
        gobject.GObject.__init__(self)
        self.queue = queue
        self.stopevent = threading.Event()

    def run(self):
        if self.queue is None:
            raise RuntimeError('Listener must be associated with a Queue')
        while not self.stopevent.isSet():
            # Listen for results on the queue and process them accordingly                            
            data = self.queue.get()
            # Check if finished                                                                       
            if data[1] == "finished":
                self.emit("finished")
                self.stop()
            elif data[0] == "error":
                self.emit('error', data[1])
                self.stop()
            else:
                self.emit('updated', data[0], data[1])

    def stop(self):
        self.stopevent.set()


class IndeterminateListener(Listener):

    def run(self):
        if self.queue is None:
            raise RuntimeError('Listener must be associated with a Queue')
        while not self.stopevent.isSet():
            # Listen for results on the queue and process them accordingly
            try:
                data = self.queue.get(True, 0.1)
            except Queue.Empty:
                self.emit('updated', 0, "")
                continue
            # Check if fin)shed                                                                       
            if data[0] == 1.0:
                self.emit("finished")
                self.stop()
            elif data[0] == "error":
                self.emit("error", data[1])
                self.stop()
            else:
                self.emit('updated', data[0], data[1])


gobject.type_register(Listener)


class BlockingWorker(Queueable):

    def __init__(self, task, *args, **kwargs):
        self.set_task(task, *args, **kwargs)

    def set_task(self, func, *args, **kwargs):
        self.task = {
            'callable': func,
            'args': args,
            'kwargs': kwargs
        }

    def run_task(self):
        t = self.task['callable']
        a = self.task['args']
        k = self.task['kwargs']
        t(*a, **k)

    def run(self, *args, **kwargs):
        if self.queue is None:
            raise RuntimeError('Listener must be associated with a Queue')
        self.queue.put((0.0, "Queue Starting..."))
        try:
            self.run_task(*args, **kwargs)
        except Exception, msg:
            self.queue.put(("error", str(msg)))
        self.queue.put((1.0, "Queue finished"))


class GeneratorWorker(BlockingWorker):

    def run(self):
        self.queue.put((0.0, "Queue Starting..."))
        for obj in self.run_task():
            self.queue.put((proportion, "working..."))
        self.queue.put((1.0, "Queue finished"))


class Dialog(gtk.MessageDialog):


    def __init__(self, message, worker, listener, parent=None):
        flags = gtk.DIALOG_MODAL if parent else 0
        super(Dialog, self).__init__(
            parent, flags, gtk.MESSAGE_INFO, gtk.BUTTONS_CANCEL, message
        )
        self.autoclose = True
        self.standalone = False

        self.progress = gtk.ProgressBar()
        self.progress.set_pulse_step(0.05)
        self.progress.show()
        self.get_message_area().pack_end(self.progress)

        # SIGNALS
        self.connect("destroy", self.on_close)
        self.connect("response", self.on_response)
        self.connect("close", self.on_close)

        # LOGIC
        self.process = None
        self.worker = worker
        self.listener = listener

    def set_worker(self, worker):
        self.worker = worker

    def set_listener(self, listener):
        self.listener = listener

    def open(self):
        gtk.gdk.threads_init()
        gtk.gdk.threads_enter()
        self.start()
        r = self.run()
        gtk.gdk.threads_leave()
        return r

    def start(self):   
        if self.process is not None:
            return
        # Creating shared Queue
        self.queue = multiprocessing.Queue()
        self.worker.queue = self.queue
        self.listener.queue = self.queue
        # Connecting Listener
        self.listener.connect("updated", self.on_progress_update)
        self.listener.connect("finished", self.on_progress_finished)
        self.listener.connect("error", self.on_progress_error)
        # Starting Listener
        self.thread = threading.Thread(target=self.listener.run, args=())
        self.thread.start()
        # Starting Worker
        self.process = multiprocessing.Process(target=self.worker.run, args=())
        self.process.start()
        # Show window
        self.show_all()

    def close(self, widget, data=None):
        if self.process:
            self.process.terminate()
        self.listener.stop()
        self.queue.close()
        self.destroy()

    def on_response(self, widget, response_id, data=None):
        if response_id == gtk.RESPONSE_CANCEL:
            self.close(widget)
        elif response_id == gtk.RESPONSE_DELETE_EVENT:
            self.close(widget)

    def on_close(self, widget, data=None):
        self.close(widget)

    def on_progress_update(self, obj, fraction, text, data=None):
        self.progress.pulse()
        self.progress.set_text(text)
        #self.progress.set_fraction(fraction)

    def on_progress_finished(self, obj, data=None):
        if self.process is None:
            raise RuntimeError("No worker process started")
        # All done: joining worker process"
        self.listener.stop()
        self.process.join()
        #self.process = None
        self.progress.set_fraction(1.0)
        self.progress.set_text("Done")
        if self.autoclose:
            self.close(None)

    def on_progress_error(self, obj, msg, data=None):
        d = uxm.dialogs.error.Dialog(msg)
        self.close(None)



def indeterminate(message, task, *args, **kwargs):
    try:
        worker = BlockingWorker(task, *args, **kwargs)
        listener = IndeterminateListener()
        dlg = Dialog(message, worker, listener)
        dlg.open()
    except Exception, e:
        uxm.dialogs.error.Dialog(str(e))
