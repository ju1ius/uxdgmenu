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

import xdg.BaseDirectory
import gtk, gio
import uxm.adapters as adapters
#adapter = adapters.get_default_adapter()
from uxm.adapters import xdg_adapter
adapter = xdg_adapter.XdgAdapter
#from uxm.adapters import gmenu_adapter
#adapter = gmenu_adapter.GmenuAdapter

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

    def __init__(self, menu_files):
        gtk.TreeStore.__init__(self,
            bool, int, str, str, gio.Icon, str, bool, bool, object
        )

        self.entries_list_iter = None
        
        if(len(menu_files) < 1):
            menu_files = ["uxm-applications.menu"]

        for menu_file in menu_files:

            filepaths = lookup_menu_files(menu_file)
            if not filepaths: continue

            menu = adapter()
            root = menu.parse(
                filepaths[0],
                adapters.INCLUDE_EXCLUDED | adapters.SORT_DISPLAY_NAME
            )
            self.__append_directory(root, None, False, menu_file)

            if len(filepaths) > 1:
                system_menu = adapter()
                root = system_menu.parse(
                    filepaths[-1],
                    adapters.INCLUDE_EXCLUDED | adapters.SORT_DISPLAY_NAME
                )
                self.__append_directory(root, None, False, menu_file)

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
