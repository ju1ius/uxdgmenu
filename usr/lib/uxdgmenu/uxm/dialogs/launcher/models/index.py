from locale import strxfrm
from operator import itemgetter

from .trie import Trie


def cmp_exact(a, b):
    if a['exact'] and not b['exact']:
        return -1
    if b['exact'] and not a['exact']:
        return 1
    if 'score' in a:
        if a['score'] < b['score']:
            return 1
        if a['score'] > b['score']:
            return -1
    return 0


def cmp_score(a, b):
    if a['score'] < b['score']:
        return -1
    if a['score'] > b['score']:
        return 1
    return cmp(strxfrm(a['prefix']), strxfrm(b['prefix']))


def unique(seq):
    seen = set()
    return [x for x in seq if x not in seen and not seen.add(x)]


def iter_unique(seq):
    seen = set()
    return (x for x in seq if x not in seen and not seen.add(x))


def intersect(first=None, *rest):
    out = []
    if not first:
        return out
    ulist = unique(first)
    if not rest:
        return ulist
    #rest = set.intersection(*map(set, rest))
    for elem in ulist:
        in_intersect = True
        for r in rest:
            in_intersect = in_intersect and elem in r
        if in_intersect:
            out.append(elem)
    return out


class Index(object):

    def __init__(self):
        self.tree = Trie()

    def add(self, word, data):
        self.tree.insert(word, data)

    def find(self, terms):
        results = []
        for term in terms:
            term_res = []
            keys = self.tree.find_keys(term)
            for k in keys:
                n = self.tree.find(k)
                for value in n.values:
                    v = value.copy()
                    v['exact'] = (term == k)
                    term_res.append(v)
            term_res.sort(key=itemgetter('exact'), reverse=True)
            #term_res.sort(cmp=cmp_exact)
            results.append([r['id'] for r in term_res])
        return intersect(*results)

    def score(self, terms):
        results = []
        for term in terms:
            term_res = []
            scores = self.tree.score(term)
            scores.sort(key=itemgetter('score'))
            #scores.sort(cmp=cmp_score)
            for scoredata in scores:
                keys = self.tree.find_keys(scoredata['prefix'])
                for k in keys:
                    n = self.tree.find(k)
                    for value in n.values:
                        v = value.copy()
                        v['exact'] = (term == k)
                        term_res.append(v)
            term_res.sort(key=itemgetter('exact'), reverse=True)
            #term_res.sort(cmp=cmp_exact)
            results.append([r['id'] for r in term_res])
        return intersect(*results)


if __name__ == "__main__":
    words = (
        "getting", "things", "gnome", "gtg",
        "google", "gtk", "gotcha", "thingamagog",
        "gamble", 'prolog', 'goofy', 'logging',
        'toggle', 'pogotage', 'gateau', 'giratoire',
        'gatage', 'geothermologie', 'gitane', 'gigantesque',
        'guitare-gratte'
    )
    idx = Index()
    for i, word in enumerate(words):
        idx.add(word, {"id": i})

    def test(word):
        res1, res2 = idx.find([word]), idx.score([word])
        #print "Test:", word
        #print ">>> Find: ", [words[i] for i in idx.find([word])]
        #print ">>> Score:", [words[i] for i in idx.score([word])]

    for i in xrange(10000):
        test('g')
        test('gtg')
        test('gta')
        test('tg')
