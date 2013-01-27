#
# Copyright(C) 2005 Red Hat, Inc.
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

import xdg.BaseDirectory, xdg.MenuEditor
import gtk, gio
import uxm.adapters as adapters
from uxm.adapters import xdg_adapter

def lookup_menu_files(filename):
    return [f for f in xdg.BaseDirectory.load_config_paths('menus/'+filename)]

class MenuTreeModel(gtk.TreeStore):
    (
        COLUMN_HIDE,
        COLUMN_TYPE,
        COLUMN_ID,
        COLUMN_NAME,
        COLUMN_ICON,
        COLUMN_MENU_FILE,
        COLUMN_SYSTEM_VISIBLE,
        COLUMN_USER_VISIBLE,
        COLUMN_OBJECT
    ) = range(9)

    COLUMN_LIST_PATH = 9

    COLUMN_TYPES = (
        bool, int, str, str, gio.Icon, str, bool, bool, object
    )

    def __init__(self, menu_file):
        gtk.TreeStore.__init__(self, *self.COLUMN_TYPES)

        if not menu_file:
            menu_file = 'uxm-applications.menu'
        self.menu_editor = xdg.MenuEditor.MenuEditor(menu_file)
        root = xdg_adapter.XdgDirectoryAdapter(self.menu_editor.menu)
        self.__append_directory(root, None, False, menu_file)

        self.entries_list_iter = None

    def to_liststore(self):
        types = self.COLUMN_TYPES + (str,)
        store = gtk.ListStore(*types)
        columns = range(self.get_n_columns())
        def add(model, path, it):
            path = self.path_to_string(path)
            row = self.get_row(it, columns) + (path,)
            store.append(row)
        self.foreach(add)
        return store

    def path_to_string(self, path):
        if isinstance(path, str):
            return path
        return ':'.join((str(p) for p in path))
    def string_to_path(self, path):
        if isinstance(path, tuple):
            return path
        return tuple(path.split(':'))

    def get_row(self, iter, columns=None):
        if not columns:
            columns = range(self.get_n_columns())
        return self.get(iter, *columns)

    def update(self, data):
        t = data['type']
        # update menu
        if adapters.TYPE_ENTRY == t:
            self.menu_editor.editMenuEntry(
                data['object'].adaptee,
                name = data['name'],
                #genericname = data['name'],
                comment = data['comment'],
                command = data['command'],
                icon = data['icon'],
                terminal = data['terminal']
            )
        elif adapters.TYPE_DIRECTORY == t:
            self.menu_editor.editMenu(
                data['object'].adaptee,
                name = data['name'],
                #genericname = data['name'],
                comment = data['comment'],
                icon = data['icon'],
            )
        # update treemodel
        it = self.get_iter_from_string(data['_path'])
        obj = self.get_value(it, self.COLUMN_OBJECT)
        icon = gio.ThemedIcon(str(obj.get_icon()), True)
        self.set(it,
            self.COLUMN_ID, obj.get_filename(),
            self.COLUMN_NAME, obj.get_display_name(),
            self.COLUMN_ICON, icon
        )

    def create(self, data):
        t = data['type']
        parent_path = data['_parent']
        parent_iter = self.get_iter_from_string(parent_path)
        parent_entry = self.get_value(parent_iter, self.COLUMN_OBJECT)
        if adapters.TYPE_ENTRY == t:
            entry = self.menu_editor.createMenuEntry(
                parent_entry and parent_entry.adaptee or None,
                data['name'],
                #genericname = data['name'],
                comment = data['comment'],
                command = data['command'],
                icon = data['icon'],
                terminal = data['terminal']
            )
        elif adapters.TYPE_DIRECTORY == t:
            entry = self.menu_editor.createMenu(
                parent_entry and parent_entry.adaptee or None,
                data['name'],
                #genericname = data['name'],
                comment = data['comment'],
                icon = data['icon'],
            )
        obj = xdg_adapter.factory(entry)
        icon = gio.ThemedIcon(str(obj.get_icon()), True)
        #FIXME: this doesn't update the view ???
        self.append(parent_iter, (
            t == adapters.TYPE_DIRECTORY,
            obj.get_type(), obj.get_display_name(),
            obj.get_display_name(), icon,
            None, True, True,
            obj
        ))

    def __append_directory(self, directory, parent_iter, system, menu_file):
        if not directory:
            return
        iter = self.iter_children(parent_iter)
        while iter is not None:
            if self.get_value(iter, self.COLUMN_ID) == directory.get_name():
                break
            iter = self.iter_next(iter)

        if iter is None:
            icon = gio.ThemedIcon(str(directory.get_icon()), True)
            type = directory.get_type()
            row = (
                type == adapters.TYPE_ENTRY,
                type, directory.get_name(),
                directory.get_display_name(), icon,
                menu_file, False, False,
                directory
            )
            iter = self.append(parent_iter, row)

        if system:
            self.set_value(iter, self.COLUMN_SYSTEM_VISIBLE, True)
        else:
            self.set_value(iter, self.COLUMN_USER_VISIBLE, True)

        for entry in directory:
            current_type = entry.get_type()

            if current_type == adapters.TYPE_DIRECTORY:
                self.__append_directory(entry, iter, system, None)
                
            if current_type != adapters.TYPE_ENTRY:
                continue
            
            child_iter = self.iter_children(iter)
            while child_iter is not None:
                if self.get_value(child_iter, self.COLUMN_TYPE) == adapters.TYPE_ENTRY and (
                   self.get_value(child_iter, self.COLUMN_ID) == entry.get_filename()
                ):
                    break
                child_iter = self.iter_next(child_iter)

            if child_iter is None:
                icon = gio.ThemedIcon(str(entry.get_icon()), True)
                type = entry.get_type()
                row = (
                    type == adapters.TYPE_ENTRY,
                    type, entry.get_filename(),
                    entry.get_display_name(), icon,
                    None, False, False,
                    entry
                )
                child_iter = self.append(iter, row)

            if system:
                self.set_value(child_iter, self.COLUMN_SYSTEM_VISIBLE, entry.is_visible(), )
            else:
                self.set_value(child_iter, self.COLUMN_USER_VISIBLE, entry.is_visible(), )
