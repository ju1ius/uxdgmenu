import os.path
import gtk

import uxm.config as config
_ = config.translate
import uxm.adapters as adapters

from . import treemodel_gtk2, filewriter_gtk2, editdialog

__DIR__ = os.path.abspath(os.path.dirname(__file__))
UI_FILE = os.path.join(__DIR__, 'ui', 'maindialog.ui')

class MenuEditorDialog:
    def __init__ (self, menu_files):
        ui = gtk.Builder()
        ui.set_translation_domain (config.PKG_NAME)
        ui.add_from_file(UI_FILE)
        self.window = ui.get_object("main_dialog")
        self.window.connect("destroy-event", self.on_destroy)
        self.window.set_icon_name("gnome-main-menu")

        for obj in ['menus_tree', 'apps_tree',
            'help_btn', 'cancel_btn', 'apply_btn',
            'add_menu_btn', 'add_app_btn', 'edit_btn',
            'move_up_btn', 'move_down_btn'
        ]:
            setattr(self, obj, ui.get_object(obj))
        ui.connect_signals(self)

        self.apps_tree.set_property('reorderable', True)
        #self.apps_tree.set_property('enable-search', True)

        self.apps_sel = self.apps_tree.get_selection()
        self.menus_sel = self.menus_tree.get_selection()

        self.edit_dialog = editdialog.EditDialog()
        self.edit_dialog.window.set_transient_for(self.window)

        self.menu_tree_model = treemodel_gtk2.MenuTreeModel(menu_files)
        #self.apps_tree.set_search_column(self.menu_tree_model.COLUMN_NAME)
        self.apps_tree.set_search_column(2)
        self.menu_file_writer = filewriter_gtk2.MenuFileWriter(self.menu_tree_model)

        self.current_iter = None
        self.current_path = None

        self.__setup_menus_tree()
        self.__setup_apps_tree()

        self.window.connect("response", self.on_response)
        self.window.set_default_size(800, 450)
        self.window.show()

    # SIGNALS

    def on_edit_btn_clicked(self, widget):
        data = self.gather_data()
        if data:
            self.edit_dialog.run(data)

    def gather_data(self):
        model, it = self.apps_sel.get_selected()
        if it:
            value = model.get(it, 1,2,3,4,8)
        else:
            model, it = self.menus_sel.get_selected()
            value = model.get(it, 1,2,3,4,8)
        data = {
            'type': value[0], 'id': value[1], 'name': value[2],
            'icon': value[3], 'object': value[4]
        }
        return data

    def __revert_to_system_default(self, parent_iter = None):
        model = self.menu_tree_model
        
        iter = model.iter_children (parent_iter)
        while iter is not None:
            if model.get_value(iter, model.COLUMN_TYPE) == adapters.TYPE_ENTRY:
                visible = model.get_value(iter, model.COLUMN_SYSTEM_VISIBLE)
                model.set_value(iter, model.COLUMN_USER_VISIBLE, visible)
            else:
                self.__revert_to_system_default(iter)
            iter = model.iter_next (iter)

    def on_destroy (self, dialog):
        gtk.main_quit()

    def on_response (self, dialog, response_id):
        if response_id == gtk.RESPONSE_REJECT:
            self.__revert_to_system_default()
            iter = self.menu_tree_model.get_iter_first()
            while iter is not None:
                self.menu_file_writer.queue_sync(iter)
                iter = self.menu_tree_model.iter_next(iter)
            return
        dialog.destroy()

    def __is_menu_tree_directory (self, model, iter, data):
        return model.get_value(iter, self.menu_tree_model.COLUMN_TYPE) == adapters.TYPE_DIRECTORY

    def __setup_menus_tree (self):
        self.menus_model = self.menu_tree_model.filter_new(None)
        self.menus_model.set_visible_func(self.__is_menu_tree_directory, None)
        self.menus_tree.set_model(self.menus_model)
        
        self.menus_tree.get_selection().set_mode(gtk.SELECTION_BROWSE)
        self.menus_tree.get_selection().connect("changed", self.__menus_selection_changed)
        self.menus_tree.set_headers_visible(False)

        column = gtk.TreeViewColumn(_("Name"))
        column.set_spacing(6)

        cell = gtk.CellRendererPixbuf()
        column.pack_start(cell, False)
        column.add_attribute(cell, 'gicon', self.menu_tree_model.COLUMN_ICON)

        cell = gtk.CellRendererText()
        column.pack_start(cell, True)
        column.add_attribute(cell, 'text', self.menu_tree_model.COLUMN_NAME)
                                
        self.menus_tree.append_column(column)

        self.menus_tree.expand_all()

    def __setup_apps_tree (self):
        self.apps_tree.get_selection().set_mode (gtk.SELECTION_SINGLE)
        self.apps_tree.set_headers_visible(True)

        column = gtk.TreeViewColumn(_("Show"))
        self.apps_tree.append_column(column)
        
        cell = gtk.CellRendererToggle()
        cell.connect("toggled", self.__on_hide_toggled)
        column.pack_start(cell, False)
        column.add_attribute(cell, 'active', self.menu_tree_model.COLUMN_USER_VISIBLE)

        column = gtk.TreeViewColumn(_("Name"))
        column.set_spacing(6)
        self.apps_tree.append_column(column)

        cell = gtk.CellRendererPixbuf()
        column.pack_start(cell, False)
        column.add_attribute(cell, 'gicon', self.menu_tree_model.COLUMN_ICON)

        cell = gtk.CellRendererText()
        column.pack_start(cell, True)
        column.add_attribute(cell, 'text', self.menu_tree_model.COLUMN_NAME)

    def __on_hide_toggled(self, toggle, path):
        def toggle_value(model, iter, column):
            value = model.get_value(iter, column)
            model.set_value(iter, column, not value)

        child_path = self.entries_model.convert_path_to_child_path(path)
        child_iter = self.menu_tree_model.get_iter(child_path)
        
        toggle_value(self.menu_tree_model, child_iter, self.menu_tree_model.COLUMN_USER_VISIBLE)

        self.menu_file_writer.queue_sync(child_iter)

    def __menus_selection_changed(self, selection):
        model, iter = selection.get_selected()
        if iter is None:
            self.apps_tree.set_model(None)
            return

        iter = model.convert_iter_to_child_iter(iter)
        
        self.entries_model = self.menu_tree_model.filter_new(self.menu_tree_model.get_path(iter))
        self.entries_model.set_visible_column(self.menu_tree_model.COLUMN_HIDE)
        self.apps_tree.set_model(self.entries_model)
