import xdg.Menu

def pu(*args):
    print unicode(u''.join(args))

def print_dir(entry, l):
    i = "  " * l
    pu(i + "+==MENU")
    pu(i, "|- name: " +  repr(entry.getName()))
    pu(i + "|- id:", entry.Name)
    pu(i + "|- icon:", entry.getIcon())
    de = entry.Directory
    pu(i + "|- file:" + (de and de.DesktopEntry.filename or "None"))
    pu(i + "|")
    pu(i + " \\")
    for e in entry.getEntries():
        if isinstance(e, xdg.Menu.Separator):
            print_sep(e, l+1)
        elif isinstance(e, xdg.Menu.Menu):
            print_dir(e, l+1)
        elif isinstance(e, xdg.Menu.MenuEntry):
            print_app(e, l+1)

def print_app(entry, l):
    i = "  "*l
    de = entry.DesktopEntry
    pu(i + "+==APP")
    pu(i + "|- name:" + repr(de.getName()))
    pu(i + "|- file:", de.getFileName())
    pu(i + "|- exec:", de.getExec())
    pu(i + "|- icon:", de.getIcon())
    pu(i + "|- term:" + str(de.getTerminal()))
    pu(i + "+- viz:",  str(entry.Show == True))

def print_sep(entry, l):
    i = "  " * l
    n = 90 - len(i)
    print
    pu(i + "=" * n)
    print

def print_menu():
    root = xdg.Menu.parse('uxm-applications.menu')
    print_dir(root, 0)



print_menu()
