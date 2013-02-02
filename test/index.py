import sys
import os
sys.path.insert(0, os.path.dirname(__file__)+'/../usr/lib/uxdgmenu')

import uxm.dialogs.launcher.models.index as index

words = (
    "getting", "things", "gnome", "gtg",
    "google", "gtk", "gotcha", "thingamagog",
    "gamble", 'prolog', 'goofy', 'logging',
    'toggle', 'pogotage', 'gateau', 'giratoire',
    'gatage', 'geothermologie', 'gitane', 'gigantesque',
    'guitare-gratte'
)
idx = index.Index()
for i, word in enumerate(words):
    idx.add(word, {"id": i})


def test(word):
    res1, res2 = idx.find([word]), idx.score([word])
    #print "Test:", word
    #print ">>> Find: ", [words[i] for i in idx.find([word])]
    #print ">>> Score:", [words[i] for i in idx.score([word])]


for i in xrange(10000):
    test('g')
    test('gt')
    test('gtg')
    test('tg')
