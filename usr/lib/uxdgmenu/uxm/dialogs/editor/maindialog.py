import os
import gtk

import uxm.config as config
_ = config.translate
import uxm.adapters as adapters

from . import treemodel, filewriter, editdialog
import uxm.dialogs.helpers as helpers

__DIR__ = os.path.abspath(os.path.dirname(__file__))
UI_FILE = os.path.join(__DIR__, 'maindialog.ui')

class MenuEditorDialog(helpers.BuildableWidgetDecorator):

    def __init__ (self, menu_file):
        super(MenuEditorDialog, self).__init__(UI_FILE, 'main_dialog')
        self.ui.set_translation_domain (config.PKG_NAME)
        self.widget.connect("destroy-event", self.on_destroy)
        self.widget.set_icon_name("gnome-main-menu")

        self.add_ui_widgets(
            'menus_tree', 'apps_tree',
            'help_btn', 'cancel_btn', 'apply_btn',
            'add_item_btn', 'add_item_type_select', 'edit_btn',
            'move_up_btn', 'move_down_btn',
            'search_entry'
        )
        self.add_item_type_select = helpers.ComboBoxTextDecorator(self.add_item_type_select)
        for s in ('Submenu', 'Application', 'Separator'):
            self.add_item_type_select.append_text(s)
        self.add_item_type_select.set_active(0)

        self.connect_signals()

        self.apps_sel = self.apps_tree.get_selection()
        self.menus_sel = self.menus_tree.get_selection()

        self.edit_dialog = editdialog.EditDialog()
        self.edit_dialog.set_transient_for(self.widget)

        self.menu_tree_model = treemodel.MenuTreeModel(menu_file)
        self.menu_file_writer = filewriter.MenuFileWriter(self.menu_tree_model)

        self.current_iter = None
        self.current_path = None

        self.__setup_menus_tree()
        self.__setup_apps_tree()

        self.widget.connect("response", self.on_response)
        self.widget.set_default_size(800, 450)
        self.widget.show_all()

    def run(self):
        response = self.widget.run()
        return response

    ###########################################################################
    # ------------------------------ SIGNALS
    ###########################################################################

    def on_destroy(self, dialog):
        gtk.main_quit()

    def on_apply_btn_clicked(self, widget, data=None):
        pass
    def on_cancel_btn_clicked(self, widget, data=None):
        pass
    def on_help_btn_clicked(self, widget, data=None):
        pass
    def on_move_down_btn_clicked(self, widget, data=None):
        pass
    def on_move_up_btn_clicked(self, widget, data=None):
        pass

    def on_response(self, dialog, response_id):
        if response_id == gtk.RESPONSE_REJECT:
            self.__revert_to_system_default()
            iter = self.menu_tree_model.get_iter_first()
            while iter is not None:
                self.menu_file_writer.queue_sync(iter)
                iter = self.menu_tree_model.iter_next(iter)
            return
        dialog.destroy()

    def on_hide_toggled(self, toggle, path):
        def toggle_value(model, iter, column):
            value = model.get_value(iter, column)
            model.set_value(iter, column, not value)

        entries_filter_model = self.apps_tree.get_model()
        entries_model = entries_filter_model.get_model()
        # Search mode
        if isinstance(entries_model, gtk.ListStore):
            child_path = entries_filter_model.convert_path_to_child_path(path)
            child_iter = entries_model.get_iter(child_path)
            toggle_value(entries_model, child_iter, self.menu_tree_model.COLUMN_USER_VISIBLE)
            original_path = entries_model.get_value(child_iter, 9)
            child_iter = self.menu_tree_model.get_iter_from_string(original_path)
        # Normal mode
        else:
            child_path = entries_filter_model.convert_path_to_child_path(path)
            child_iter = self.menu_tree_model.get_iter(child_path)
        
        toggle_value(self.menu_tree_model, child_iter, self.menu_tree_model.COLUMN_USER_VISIBLE)

        self.menu_file_writer.queue_sync(child_iter)

    def menus_selection_changed(self, selection):
        model, iter = selection.get_selected()
        if iter is None:
            self.apps_tree.set_model(None)
            return

        iter = model.convert_iter_to_child_iter(iter)
        
        self.entries_model = self.menu_tree_model.filter_new(self.menu_tree_model.get_path(iter))
        self.entries_model.set_visible_column(self.menu_tree_model.COLUMN_HIDE)
        self.apps_tree.set_model(self.entries_model)

    def on_search_entry_focus_in(self, widget, data=None):
        store = self.menu_tree_model.to_liststore()
        filter = store.filter_new()
        filter.set_visible_func(self.search_callback)
        self.apps_tree.set_model(filter)

    def search_callback(self, model, it, data=None):
        text = self.search_entry.get_text()
        if not text:
            return False
        pattern = text.lower()
        name = model.get_value(it, 3)
        return name.lower().find(pattern) != -1

    def on_search_entry_changed(self, widget, data=None):
        self.apps_tree.get_model().refilter()

    def on_add_item_btn_clicked(self, widget):
        item_type = self.add_item_type_select.get_active()
        # ----- find parent path
        model, it = self.menus_tree.get_selection().get_selected()
        menus_filter_model = self.menus_tree.get_model()
        menus_model = menus_filter_model.get_model()
        child_iter = menus_filter_model.convert_iter_to_child_iter(it)
        parent_path = menus_model.get_path(child_iter)
        # -----
        response = self.edit_dialog.run({
            'is_new': True,
            'type': item_type + 1,
            '_parent': self.menu_tree_model.path_to_string(parent_path)
        })
        if response == gtk.RESPONSE_ACCEPT:
            data = self.edit_dialog.get_data()
            self.menu_tree_model.create(data)
        print "response %s from result of run()" % response

    def on_edit_btn_clicked(self, widget):
        data = self.__gather_data()
        if data:
            response = self.edit_dialog.run(data)
            print "response %s from result of run()" % response
            if response == gtk.RESPONSE_ACCEPT:
                data = self.edit_dialog.get_data()
                self.menu_tree_model.update(data)

    ###########################################################################
    # ------------------------------ PRIVATE
    ###########################################################################

    def __gather_data(self):
        model, it = self.apps_tree.get_selection().get_selected()
        # get row values and path from actual model
        if it:
            value = model.get(it, 1,2,3,4,8)
            entries_filter_model = self.apps_tree.get_model()
            entries_model = entries_filter_model.get_model()
            if isinstance(entries_model, gtk.ListStore):
                child_iter = entries_filter_model.convert_iter_to_child_iter(it)
                path = entries_model.get_value(child_iter, self.menu_tree_model.COLUMN_LIST_PATH)
                parent_iter = self.menu_tree_model.iter_parent(
                    self.menu_tree_model.get_iter_from_string(path)
                )
                parent_path = self.menu_tree_model.get_path(parent_iter)
            else:
                child_iter = entries_filter_model.convert_iter_to_child_iter(it)
                path = entries_model.get_path(child_iter)
                parent_iter = entries_model.iter_parent(child_iter)
                parent_path = entries_model.get_path(parent_iter)
        else:
            model, it = self.menus_tree.get_selection().get_selected()
            value = model.get(it, 1,2,3,4,8)
            menus_filter_model = self.menus_tree.get_model()
            menus_model = menus_filter_model.get_model()
            child_iter = menus_filter_model.convert_iter_to_child_iter(it)
            path = menus_model.get_path(child_iter)
            parent_iter = menus_model.iter_parent(child_iter)
            parent_path = menus_model.get_path(parent_iter)
        obj = value[4]
        data = {
            'type': value[0], 'id': value[1], 'name': value[2],
            'icon': obj.get_icon(), 'object': obj,
            'is_new': False,
            '_path': self.menu_tree_model.path_to_string(path),
            '_parent': self.menu_tree_model.path_to_string(parent_path)
        }
        return data

    def __revert_to_system_default(self, parent_iter = None):
        model = self.menu_tree_model
        
        iter = model.iter_children(parent_iter)
        while iter is not None:
            if model.get_value(iter, model.COLUMN_TYPE) == adapters.TYPE_ENTRY:
                visible = model.get_value(iter, model.COLUMN_SYSTEM_VISIBLE)
                model.set_value(iter, model.COLUMN_USER_VISIBLE, visible)
            else:
                self.__revert_to_system_default(iter)
            iter = model.iter_next(iter)

    def __is_menu_tree_directory(self, model, iter, data):
        return model.get_value(iter, self.menu_tree_model.COLUMN_TYPE) == adapters.TYPE_DIRECTORY

    def __setup_menus_tree(self):
        self.menus_model = self.menu_tree_model.filter_new(None)
        self.menus_model.set_visible_func(self.__is_menu_tree_directory, None)
        self.menus_tree.set_model(self.menus_model)
        
        self.menus_tree.get_selection().set_mode(gtk.SELECTION_BROWSE)
        self.menus_tree.get_selection().connect("changed", self.menus_selection_changed)
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
        self.apps_tree.get_selection().set_mode(gtk.SELECTION_SINGLE)
        self.apps_tree.set_headers_visible(True)

        column = gtk.TreeViewColumn(_("Show"))
        self.apps_tree.append_column(column)
        
        cell = gtk.CellRendererToggle()
        cell.connect("toggled", self.on_hide_toggled)
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
