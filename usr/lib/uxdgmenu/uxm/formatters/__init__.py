import sys

TYPE_TREE = 0
TYPE_FLAT = 1

def get_formatter(name):
    module = __import__(name, globals())
    formatter = getattr(module, 'Formatter')
    return formatter()
