import pygtk
pygtk.require('2.0')
import gtk

class Dialog(gtk.MessageDialog):
    def __init__(self, message):
        super(Dialog, self).__init__(
            type = gtk.MESSAGE_ERROR,
            flags = gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            message_format = "Error:", buttons = gtk.BUTTONS_OK
        )
        self.format_secondary_text(message)
        gtk.gdk.threads_enter()
        self.run()
        self.destroy() 
        gtk.gdk.threads_leave()
