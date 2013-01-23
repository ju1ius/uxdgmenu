#
# Copyright (C) 2005 Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#

import os.path
from gi.repository import Gtk

import uxm.config as config
_ = config.translate

from . import menutreemodel
from . import menufilewriter

__DIR__ = os.path.abspath(os.path.dirname(__file__))
UI_FILE = os.path.join(__DIR__, 'editor.ui')

class MenuEditorDialog:
    def __init__ (self, menu_files):
        self.ui = Gtk.Builder()
        self.ui.set_translation_domain (config.PKG_NAME)
        self.ui.add_from_file(UI_FILE)
        self.window = self.ui.get_object ("menu_editor_dialog")
        self.window.connect ("destroy", self.__dialog_destroyed)
        self.window.set_default_response (Gtk.ResponseType.ACCEPT)
        self.window.set_icon_name ("gnome-main-menu")

        self.help_button = self.ui.get_object ("help_button")
        self.help_button.set_sensitive (False)

        self.menus_tree   = self.ui.get_object ("menus_treeview")
        self.entries_list = self.ui.get_object ("applications_treeview")

        self.menu_tree_model = menutreemodel.MenuTreeModel (menu_files)
        
        self.menu_file_writer = menufilewriter.MenuFileWriter (self.menu_tree_model)

        self.current_iter = None
        self.current_path = None

        self.__setup_menus_tree ()
        self.__setup_entries_list ()

        self.window.connect ("response", self.__dialog_response)
        self.window.set_default_size (580, 435)
        self.window.show ()

    def __revert_to_system_default (self, parent_iter = None):
        model = self.menu_tree_model
        
        iter = model.iter_children (parent_iter)
        while iter is not None:
            if model.get_value (iter, model.COLUMN_IS_ENTRY):
                visible = model.get_value (iter, model.COLUMN_SYSTEM_VISIBLE)
                model.set_value (iter, model.COLUMN_USER_VISIBLE, visible)
            else:
                self.__revert_to_system_default (iter)
            
            iter = model.iter_next (iter)

    def __dialog_destroyed (self, dialog):
        Gtk.main_quit ()

    def __dialog_response (self, dialog, response_id):
        if response_id == Gtk.ResponseType.REJECT:
            self.__revert_to_system_default ()
            iter = self.menu_tree_model.get_iter_first ()
            while iter is not None:
                self.menu_file_writer.queue_sync (iter)
                iter = self.menu_tree_model.iter_next (iter)
            return
        
        dialog.destroy ()

    def __is_menu_tree_directory (self, model, iter, data):
        return not model.get_value(iter, self.menu_tree_model.COLUMN_IS_ENTRY)

    def __setup_menus_tree (self):
        self.menus_model = self.menu_tree_model.filter_new (None)
        self.menus_model.set_visible_func (self.__is_menu_tree_directory, None)
        self.menus_tree.set_model (self.menus_model)
        
        self.menus_tree.get_selection ().set_mode (Gtk.SelectionMode.BROWSE)
        self.menus_tree.get_selection ().connect ("changed", self.__menus_selection_changed)
        self.menus_tree.set_headers_visible (False)

        column = Gtk.TreeViewColumn (_("Name"))
        column.set_spacing (6)

        cell = Gtk.CellRendererPixbuf ()
        column.pack_start (cell, False)
        column.add_attribute (cell, 'gicon', self.menu_tree_model.COLUMN_ICON)

        cell = Gtk.CellRendererText ()
        column.pack_start (cell, True)
        column.add_attribute (cell, 'text', self.menu_tree_model.COLUMN_NAME)
                                
        self.menus_tree.append_column (column)

        self.menus_tree.expand_all ()

    def __setup_entries_list (self):
        self.entries_list.get_selection ().set_mode (Gtk.SelectionMode.SINGLE)
        self.entries_list.set_headers_visible (True)

        column = Gtk.TreeViewColumn (_("Show"))
        self.entries_list.append_column (column)
        
        cell = Gtk.CellRendererToggle ()
        cell.connect ("toggled", self.__on_hide_toggled)
        column.pack_start (cell, False)
        column.add_attribute (cell, 'active', self.menu_tree_model.COLUMN_USER_VISIBLE)

        column = Gtk.TreeViewColumn (_("Name"))
        column.set_spacing (6)
        self.entries_list.append_column (column)

        cell = Gtk.CellRendererPixbuf ()
        column.pack_start (cell, False)
        column.add_attribute (cell, 'gicon', self.menu_tree_model.COLUMN_ICON)

        cell = Gtk.CellRendererText ()
        column.pack_start (cell, True)
        column.add_attribute (cell, 'text', self.menu_tree_model.COLUMN_NAME)

    def __on_hide_toggled (self, toggle, path):
        def toggle_value (model, iter, column):
            value = model.get_value (iter, column)
            model.set_value (iter, column, not value)

        real_path = Gtk.TreePath.new_from_string (path)
        child_path = self.entries_model.convert_path_to_child_path (real_path)
        child_iter = self.menu_tree_model.get_iter (child_path)
        
        toggle_value (self.menu_tree_model, child_iter, self.menu_tree_model.COLUMN_USER_VISIBLE)

        self.menu_file_writer.queue_sync (child_iter)

    def __menus_selection_changed (self, selection):
        (model, iter) = selection.get_selected ()
        if iter is None:
            self.entries_list.set_model (None)
            return

        iter = model.convert_iter_to_child_iter (iter)
        
        self.entries_model = self.menu_tree_model.filter_new (self.menu_tree_model.get_path (iter))
        self.entries_model.set_visible_column (self.menu_tree_model.COLUMN_IS_ENTRY)
        self.entries_list.set_model (self.entries_model)
