import os
import gtk

import uxm.config as config
import uxm.adapters as adapters

__DIR__ = os.path.abspath(os.path.dirname(__file__))
UI_FILE = os.path.join(__DIR__, 'ui', 'editdialog.ui')

class EditDialog(object):

    def __init__(self):
        ui = gtk.Builder()
        ui.set_translation_domain (config.PKG_NAME)
        ui.add_from_file(UI_FILE)
        self.window = ui.get_object ("edit_dialog")

        for obj in ['name_entry', 'cmd_entry', 'cmd_chooser_btn', 'cmd_term_cb',
            'icn_entry', 'icn_chooser_btn', 'apply_edit_btn', 'cancel_edit_btn'
        ]:
            setattr(self, obj, ui.get_object(obj))

        self.cmd_chooser_btn.set_current_folder('/usr/bin')

        ui.connect_signals(self)

    def run(self, data):
        self.populate_fields(data)
        self.window.run()

    def populate_fields(self, data):
        self.name_entry.set_text(data['name'])
        obj = data['object']
        icon = data['icon']
        self.icn_entry.set_text(str(icon.get_names()))
        if data['type'] == adapters.TYPE_ENTRY:
            self.cmd_entry.set_text(obj.get_exec())
            self.cmd_term_cb.set_active(obj.is_terminal())

    # SIGNALS

    def on_response(self, widget, response_id):
        print response_id
        if response_id == gtk.RESPONSE_ACCEPT:
            data = {
                'name': self.name_entry.get_text(),
                'command': self.cmd_entry.get_text(),
                'terminal': self.cmd_term_cb.get_active(),
                'icon': self.icn_entry.get_text(),
                'category': ''
            }
            print data
            self.window.hide()
        elif response_id == gtk.RESPONSE_REJECT:
            self.window.hide()
        elif response_id == gtk.RESPONSE_DELETE_EVENT:
            self.window.hide()
            return True
        return False


    def on_apply_edit_btn_clicked(self, widget):
        pass

    def on_cancel_edit_btn_clicked(self, widget):
        pass

    def on_cmd_chooser_btn_file_set(self, widget):
        self.cmd_entry.set_text(widget.get_filename())
        pass
