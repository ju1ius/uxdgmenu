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
from gi.repository import GObject, Gio, Gtk
#from gi.repository import GMenu
import uxm.adapters as adapters
#adapter = adapters.get_default_adapter()
from uxm.adapters import xdg_adapter
adapter = xdg_adapter.XdgAdapter

def lookup_menu_files(filename):
    return [f for f in xdg.BaseDirectory.load_config_paths('menus/'+filename)]

class MenuTreeModel(Gtk.TreeStore):
    (
        COLUMN_IS_ENTRY,
        COLUMN_ID,
        COLUMN_NAME,
        COLUMN_ICON,
        COLUMN_MENU_FILE,
        COLUMN_SYSTEM_VISIBLE,
        COLUMN_USER_VISIBLE
    ) = range(7)

    def __init__(self, menu_files):
        Gtk.TreeStore.__init__(self, bool, str, str, Gio.Icon, str, bool, bool)

        self.entries_list_iter = None
        
        if(len(menu_files) < 1):
            menu_files = ["uxm-applications.menu"]

        for menu_file in menu_files:

            filepaths = lookup_menu_files(menu_file)
            if not filepaths: continue

            tree = adapter()
            #tree = GObject.new(
                #GMenu.Tree,
                #menu_path = filepaths[0],
                #flags = GMenu.TreeFlags.INCLUDE_EXCLUDED | GMenu.TreeFlags.SORT_DISPLAY_NAME
            #)
            #tree.load_sync()
            #self.__append_directory(tree.get_root_directory(), None, True, menu_file)
            root = tree.get_root_directory(filepaths[0],
                    adapters.INCLUDE_EXCLUDED | adapters.SORT_DISPLAY_NAME)
            self.__append_directory(root, None, False, menu_file)

            if len(filepaths) > 1:
                #system_tree = GObject.new(
                    #GMenu.Tree,
                    #menu_path = filepaths[-1],
                    #flags = GMenu.TreeFlags.INCLUDE_EXCLUDED | GMenu.TreeFlags.SORT_DISPLAY_NAME
                #)
                #system_tree.load_sync()
                #self.__append_directory(system_tree.get_root_directory(), None, True, menu_file)
                system_tree = adapter()
                root = system_tree.get_root_directory(filepaths[-1],
                        adapters.INCLUDE_EXCLUDED | adapters.SORT_DISPLAY_NAME)
                self.__append_directory(root, None, False, menu_file)

    def __append_directory(self, directory, parent_iter, system, menu_file):
        if not directory:
            return
        iter = self.iter_children(parent_iter)
        while iter is not None:
            if self.get_value(iter, self.COLUMN_ID) == directory.Directory:
                break
            iter = self.iter_next(iter)

        if iter is None:
            icon = Gio.ThemedIcon.new_with_default_fallbacks(directory.getIcon())
            row = (False, directory.Directory, directory.Name, icon, menu_file, False, False)
            iter = self.append(parent_iter, row)

        if system:
            self.set_value(iter, self.COLUMN_SYSTEM_VISIBLE, True)
        else:
            self.set_value(iter, self.COLUMN_USER_VISIBLE, True)

        print directory
        #dir_iter = directory.iter()
        #next_type = dir_iter.next()
        #while next_type:# != GMenu.TreeItemType.INVALID:
        for entry in directory:
            #current_type = next_type
            #next_type = dir_iter.next()
            current_type = entry.get_type()

            #if current_type == GMenu.TreeItemType.DIRECTORY:
            if current_type == adapters.TYPE_DIRECTORY:
                self.__append_directory(entry, iter, system, None)
                #child_item = directory.get_directory()
                #self.__append_directory(child_item, iter, system, None)
                
            #if current_type != GMenu.TreeItemType.ENTRY:
            if current_type != adapters.TYPE_ENTRY:
                continue
            
            #child_item = directory.get_entry()

            child_iter = self.iter_children(iter)
            while child_iter is not None:
                if self.get_value(child_iter, self.COLUMN_IS_ENTRY) and \
                   self.get_value(child_iter, self.COLUMN_ID) == entry.Filename:
                   #self.get_value(child_iter, self.COLUMN_ID) == child_item.get_desktop_file_id():
                        break
                child_iter = self.iter_next(child_iter)

            if child_iter is None:
                icon = Gio.ThemedIcon.new_with_default_fallbacks(entry.getIcon())
                row = (True, entry.Filename,
                        entry.Name, icon, None, False, False)
                #app_info = child_item.get_app_info()
                #row = (True, child_item.get_desktop_file_id(), app_info.Name, app_info.getIcon(), None, False, False)
                child_iter = self.append(iter, row)

            if system:
                self.set_value(child_iter, self.COLUMN_SYSTEM_VISIBLE, not
                        child_item.isVisible(),)
            else:
                self.set_value(child_iter, self.COLUMN_USER_VISIBLE, not
                        child_item.isVisible(),)
