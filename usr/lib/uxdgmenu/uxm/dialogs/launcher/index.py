from .trie import Trie


def cmp(a, b):
    if a['exact'] and not b['exact']:
        return -1
    if b['exact'] and not a['exact']:
        return 1
    if 'score' in a:
        if a['score'] < b['score']:
            return 1;
        if a['score'] > b['score']:
            return -1
    return 0;

def unique(seq):
    seen = set()
    return [x for x in seq if x not in seen and not seen.add(x)]

def intersect(first=None, *rest):
    out = []
    if not first:
        return out
    ulist = unique(first)
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
            term_res.sort(cmp=cmp)
            results.append([r['id'] for r in term_res])
        return intersect(*results)


