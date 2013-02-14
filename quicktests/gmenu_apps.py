import gmenu

def print_dir(entry, l):
    i = "  " * l
    print i + "+==MENU"
    print i + "|- name:", entry.get_name()
    print i + "|- id:", entry.get_menu_id()
    print i + "|- icon:", entry.get_icon()
    print i + "|- file:", entry.get_desktop_file_path()
    print i + "|"
    print i + " \\"
    for e in entry.get_contents():
        t = e.get_type()
        if t == gmenu.TYPE_SEPARATOR:
            print_sep(e, l+1)
        elif t == gmenu.TYPE_DIRECTORY:
            print_dir(e, l+1)
        elif t == gmenu.TYPE_ENTRY:
            print_app(e, l+1)

def print_app(entry, l):
    i = "  "*l
    print i + "+==APP"
    print i + "|- name:", entry.get_display_name()
    print i + "|- file:", entry.get_desktop_file_path()
    print i + "|- exec:", entry.get_exec()
    print i + "|- icon:", entry.get_icon()
    print i + "|- term:", entry.get_launch_in_terminal()
    print i + "+- viz:", not entry.get_is_excluded()

def print_sep(entry, l):
    i = "  " * l
    n = 90 - len(i)
    print
    print i + "=" * n
    print

def print_menu():
    tree = gmenu.lookup_tree('uxm-applications.menu')
    root = tree.get_root_directory()
    print_dir(root, 0)



print_menu()
