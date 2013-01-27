import os
import gtk

import uxm.config as config
import uxm.adapters as adapters
import uxm.dialogs.helpers as helpers
from uxm.dialogs.iconchooser import IconChooserButton

__DIR__ = os.path.abspath(os.path.dirname(__file__))
UI_FILE = os.path.join(__DIR__, 'editdialog.ui')

class EditDialog(helpers.BuildableWidgetDecorator):

    entries = ('name_entry', 'cmd_entry', 'cmd_term_cb', 'icn_entry')

    def __init__(self):
        super(EditDialog, self).__init__(UI_FILE, 'edit_dialog')
        self.ui.set_translation_domain(config.PKG_NAME)

        self.add_ui_widgets(
            'name_entry', 'cmd_entry', 'cmd_chooser_btn', 'cmd_term_cb',
            'comment_entry', 'icn_entry',
            'apply_edit_btn', 'cancel_edit_btn'
        )

        icn_box = self.ui.get_object('icn_hbox')
        self.icn_chooser_button = IconChooserButton(label='Choose...')
        self.icn_chooser_button.dialog.set_transient_for(self.widget)
        self.icn_chooser_button.connect('file-set', self.on_icon_chooser_btn_file_set)
        icn_box.pack_end(self.icn_chooser_button.button)

        self.cmd_chooser_btn.set_current_folder('/usr/bin')

        self.connect_signals()

    def run(self, data):
        self.populate_fields(data)
        return self.widget.run()

    def get_data(self):
        return self.__data

    def populate_fields(self, data):
        self.reset_fields()
        self.__data = data
        data_type = data['type']
        self.toggle_entry_fields(data_type == adapters.TYPE_ENTRY)
        if data['is_new']:
            return
        self.name_entry.set_text(data['name'])
        icon = data['icon']
        self.icn_entry.set_text(icon and icon or "")
        obj = data['object']
        comment = obj.get_comment()
        self.comment_entry.set_text(comment and comment or "")
        if data_type == adapters.TYPE_ENTRY:
            self.cmd_entry.set_text(obj.get_exec())
            self.cmd_term_cb.set_active(obj.is_terminal())
        elif data_type == adapters.TYPE_DIRECTORY:
            pass

    def reset_fields(self):
        for id in ('name_entry', 'cmd_entry', 'icn_entry', 'comment_entry'):
            entry = self.ui.get_object(id)
            entry.set_text('')
        self.cmd_term_cb.set_active(False)

    def toggle_entry_fields(self, show=True):
        for id in ('cmd_lbl_vbox', 'cmd_vbox'):
            self.toggle_field_visibility(self.ui.get_object(id), show)

    def toggle_field_visibility(self, field, show=True):
        method_name = show and 'show' or 'hide'
        method = getattr(field, method_name)
        method()

    def __gather_data(self):
        data = {
            'name': self.name_entry.get_text(),
            'comment': self.comment_entry.get_text(),
            'command': self.cmd_entry.get_text(),
            'terminal': self.cmd_term_cb.get_active(),
            'icon': self.icn_entry.get_text(),
            'categories': ''
        }
        return data

    # SIGNALS

    def on_response(self, widget, response_id):
        print "response %s from dialog" % response_id
        if response_id == gtk.RESPONSE_ACCEPT:
            #FIXME: handle new objects
            newdata = self.__gather_data()
            self.__data.update(newdata)
            print self.__data
            self.widget.hide()
        elif response_id == gtk.RESPONSE_REJECT:
            self.__data = None
            self.reset_fields()
            self.widget.hide()
        elif response_id == gtk.RESPONSE_DELETE_EVENT:
            self.__data = None
            self.reset_fields()
            self.widget.hide()
            return True
        return False


    def on_apply_edit_btn_clicked(self, widget):
        pass

    def on_cancel_edit_btn_clicked(self, widget):
        pass

    def on_cmd_chooser_btn_file_set(self, widget):
        self.cmd_entry.set_text(widget.get_filename())

    def on_icon_chooser_btn_file_set(self, widget, name, path):
        self.icn_entry.set_text(name)
        #self.icn_entry.set_text(path and path or name)
