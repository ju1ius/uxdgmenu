import gmenu

def printobj(obj, level=0):
    i = ">>>" * level
    print i, str(obj.__class__)
    for prop in dir(obj):
        print i + '>>>', prop, '=>', repr(getattr(obj, prop))
    print ""

tree = gmenu.lookup_tree('uxm-applications.menu')
root = tree.get_root_directory()

print ">>> ROOT"
printobj(root)

for entry in root.get_contents():
    printobj(entry, 1)
    print "\n"
    if hasattr(entry, 'get_contents'):
        for e in entry.get_contents():
            printobj(e, 2)
            print "\n"
        if hasattr(e, 'get_contents'):
            for e2 in e.get_contents():
                printobj(e2, 3)
                print "\n"

