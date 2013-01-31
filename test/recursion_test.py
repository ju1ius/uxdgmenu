import cPickle as pickle
menu = {
    'id': 'Applications',
    'type': 'menu',
    'items': [
        {'id': 'App1', 'type': 'app'},
        {'id': 'App2', 'type': 'app'},
        {'id': 'System', 'type':'menu','items':[
            {'id': 'App3:1', 'type': 'app'},
            {'id': 'App3:2', 'type': 'app'},
            {'id': 'Other', 'type':'menu','items':[
                {'id': 'App3:3:1', 'type': 'app'},
                {'id': 'App3:3:2', 'type': 'app'},
            ]}
        ]}
    ]
}

with open ('/home/ju1ius/.cache/uxdgmenu/applications.pckl', 'r') as fp:
    menu = pickle.load(fp)

def iter_menu(item):
    if item['type'] == 'application':
        yield item
    elif item['type'] == 'menu':
        for child_item in item['items']:
            for child in iter_menu(child_item):
                yield child

for app in iter_menu(menu):
    print app['label'], app['command']
