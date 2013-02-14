import xdg.Menu

root = xdg.Menu.parse('uxm-applications.menu')


def printobj(obj, level=0):
    i = ">>>" * level
    print i, str(obj.__class__)
    for prop in dir(obj):
        print i, '>>>', prop, '=>', repr(getattr(obj, prop))
    if hasattr(obj, 'DesktopEntry'):
        de = obj.DesktopEntry
        print i,  ' V - DesktopEntry'
        printobj(de, level+1)
    if hasattr(obj, 'Directory'):
        de = obj.Directory
        print i, ' V - Directory'
        printobj(de, level+1)
    print ""


print ">>> ROOT"
printobj(root)

for entry in root.getEntries():
    printobj(entry, 1)
    print "\n"
    if hasattr(entry, 'getEntries'):
        for e in entry.getEntries():
            printobj(e, 2)
            print "\n"
        if hasattr(e, 'getEntries'):
            for e2 in e.getEntries():
                printobj(e2, 3)
                print "\n"


