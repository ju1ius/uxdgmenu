

def walker(word, node):
    if not word or not node:
        return(None,None)
    for char in word:
        if char not in node.children:
            return (None,None)
        child = node.children[char]
        prev = node
        node = child
    return (prev, char)

def find_keys(term, node, lst):
    lst.append(term)
    for k, v in node.children.iteritems():
        find_keys(term + k, v, lst)

def score(term, term_len, term_pos, node, depth, match_positions, results, prefix):
    key = term[term_pos]
    children = node.children
    if key == node.key:
        match_positions.append(depth)
        if term_pos < term_len - 1:
            for k, v in children.iteritems():
                score(term, term_len, term_pos+1, v, depth+1, match_positions[:],
                        results, prefix+k)
        else:
            results.append({
                'prefix': prefix,
                'depth': depth,
                'indexes': match_positions,
                "start": match_positions[0],
                'score': sum(match_positions)
            })
    else:
        for k, v in children.iteritems():
            score(term, term_len, term_pos, v, depth+1, match_positions[:],
                    results, prefix+k)

class TrieNode(object):
    __slots__=('key', 'children', 'values')

    def __init__(self, key=None):
        self.key = key
        self.children = {}
        self.values = []

class Trie(object):
    
    def __init__(self):
        self.root = TrieNode()

    def insert(self, key, value):
        node = self.root
        for char in key:
            if char not in node.children:
                node.children[char] = TrieNode(char)
            node = node.children[char]
        node.values.append(value)

    def remove(self, word):
        parent, key = walker(word, self.root)
        del parent.children[key]

    def find(self, word):
        parent, key = walker(word, self.root)
        if parent:
            return parent.children.get(key)

    def find_keys(self, term=""):
        parent = self.find(term)
        keys = []
        if parent:
            find_keys(term, parent, keys)
        return keys

    def each(self, word):
        if not word:
            return
        node = self.root
        for char in word:
            child = node.children.get(char)
            if not child:
                return
            #prev = node
            node = child
            yield child, char

    def score(self, word):
        node = self.root
        l = len(word)
        results = []
        for k, v in node.children.iteritems():
            score(word, l, 0, v, 0, [], results, k)
        return results
