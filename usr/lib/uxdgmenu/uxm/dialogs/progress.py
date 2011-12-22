import pygtk
pygtk.require('2.0')
import gtk
import gobject
import multiprocessing, threading, Queue


class Queueable(object):
    def __init(self):
        super(Queueable, self).__init__()
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
    stopevent = threading.Event()

    def __init__(self, queue=None):
        gobject.GObject.__init__(self)
        self.queue = queue

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
            if data[0] == 1:
                self.emit("finished")
                self.stop()
            elif data[0] == "error":
                self.emit("error", data[1])
                self.stop()
            else:
                self.emit('updated', data[0], data[1])


gobject.type_register(Listener)


class BlockingWorker(Queueable):
    def __init__(self, task):
        self.task = task

    def run(self, *args, **kwargs):
        if self.queue is None:
            raise RuntimeError('Listener must be associated with a Queue')
        self.queue.put((0.0, "Queue Starting..."))
        try:
            self.task(*args, **kwargs)
        except Exception, msg:
            self.queue.put(("error", str(msg)))
        self.queue.put((1.0, "Queue finished"))


class GeneratorWorker(BlockingWorker):
    def run(self, *args, **kwargs):
        self.queue.put((0.0, "Queue Starting..."))
        for obj in self.task(*args, **kwargs):
            self.queue.put((proportion, "working..."))
        self.queue.put((1.0, "Queue finished"))


class Dialog(gtk.Window):

    def __init__(self, message, worker, listener):
        super(Dialog, self).__init__(gtk.WINDOW_TOPLEVEL)
        self.set_border_width(10)
        #self.set_default_size(400, 250)
        self.label = gtk.Label()
        self.label.set_use_markup(True)
        self.label.set_markup(message)
        
        self.progress = gtk.ProgressBar()
        self.progress.set_pulse_step(0.05)

        self.button_ok = gtk.Button(stock=gtk.STOCK_OK)
        self.button_cancel = gtk.Button(stock=gtk.STOCK_CANCEL)

        buttonbox = gtk.HButtonBox()
        buttonbox.set_spacing(5)
        buttonbox.pack_start(self.button_cancel)
        buttonbox.pack_start(self.button_ok)

        self.vbox = gtk.VBox(spacing=10)
        self.vbox.pack_start(self.label)
        self.vbox.pack_start(self.progress)
        self.vbox.pack_start(buttonbox)

        self.add(self.vbox)

        # SIGNALS
        self.connect("destroy", self.destroy)
        self.button_ok.connect("clicked", self.on_click_ok)
        self.button_cancel.connect("clicked", self.on_click_cancel)

        # LOGIC
        self.process = None
        self.worker = worker
        self.listener = listener

    def set_worker(self, worker):
        self.worker = worker
    def set_listener(self, listener):
        self.listener = listener

    def destroy(self, widget, data=None):
        if self.process:
            self.process.terminate()
        self.listener.stop()
        self.queue.close()
        gtk.main_quit()

    def on_click_ok(self, widget, data=None):
        gtk.main_quit()

    def on_click_cancel(self, widget, data=None):
        self.destroy(widget, data)

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
        self.process = None
        self.progress.set_fraction(1.0)
        self.progress.set_text("Done")
        self.button_ok.set_sensitive(True)

    def on_progress_error(self, obj, msg, data=None):
        from . import error
        d = error.Dialog(msg)
        self.destroy(None)

    def start(self):   
        if self.process is not None:
            return
        self.button_ok.set_sensitive(False)
        # Creating shared Queue
        self.queue = multiprocessing.Queue()
        self.worker.queue = self.queue
        self.listener.queue = self.queue
        # Connecting Listener
        self.listener.connect("updated", self.on_progress_update)
        self.listener.connect("finished", self.on_progress_finished)
        self.listener.connect("error", self.on_progress_error)
        # Starting Worker
        self.process = multiprocessing.Process(target=self.worker.run, args=())
        self.process.start()
        # Starting Listener
        self.thread = threading.Thread(target=self.listener.run, args=())
        self.thread.start()
        # Start GTK main loop
        self.show_all()
        gtk.gdk.threads_init()
        gtk.gdk.threads_enter()
        gtk.main()
        gtk.gdk.threads_leave()


def indeterminate(message, task):
    worker = BlockingWorker(task)
    listener = IndeterminateListener()
    gui = Dialog(message, worker, listener)
    gui.start()
