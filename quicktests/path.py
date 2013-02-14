import re
import shlex
import time

paths = [
    ('/bin/foo\ bar',['/bin/foo\ bar']),
    ('/bin/foo\ bar/', ['/bin/foo\ bar/']),
    ('/bin/foo\ bar/\\', ['/bin/foo\ bar/\\']),
    ('/bin/foo\ bar/\\ baz', ['/bin/foo\ bar/\\ baz']),
    ('/bin/foo\ bar/\\ baz\\ ', ['/bin/foo\ bar/\\ baz\\ ']),
    ('cmd ~/.config/foo/bar.cfg', ['~/.config/foo/bar.cfg']),
    ('cmd ~/My Music/Stairway To Heaven.mp3', ['~/My']),
    ('cmd ~/Documents/Dossier\ de\ Presse.doc', ['~/Documents/Dossier\ de\ Presse.doc']),
    ('cmd "/home/johndoe/new stuff"', ['/home/johndoe/new stuff']),
    ('cmd "~/music/foo bar', ['~/music/foo bar']),
    ('cmd ~/music/An\ "Album"', ['~/music/An\ "Album"']),
    ('cmd \'~/music/An "Album"\'', ['~/music/An "Album"'])
]


def shlexer(path):
    lex = shlex.shlex(path, posix=True)
    lex.whitespace_split = True
    lex.commenters = ''
    #lex.debug = 2
    tokens = []
    try:
        tok = lex.get_token()
    except:
        return [lex.token]
    while(tok != lex.eof):
        tokens.append(tok)
        try:
            tok = lex.get_token()
        except:
            tokens.append(lex.token)
            break
    return tokens


SEARCH_RX = re.compile(r'["\']?[~/](?:[^/]*/)*')


class State(object):

    INITIAL = 0x0
    NONE = 0x1
    PATH = 0x2
    QUOTE = 0x4
    DQUOTE = 0x8

    def __init__(self):
        self.value = self.INITIAL

    def reset(self):
        self.value = self.INITIAL

    def set(self, state):
        self.value = state

    def get(self):
        return self.value

    def equals(self, state):
        return self.value == state

    def is_in(self, state):
        return self.value & state == state

    def enter(self, state):
        self.value |= state

    def leave(self, state):
        self.value &= ~state

    def __eq__(self, state):
        return self.value == state

    def __contains__(self, state):
        return self.value & state == state

    def __add__(self, state):
        self.value |= state
        return self

    def __sub__(self, state):
        self.value &= ~state
        return self

    def __str__(self):
        return "<State: %s>" % self.value


ABSPATH_RX = re.compile(r'(?:/(?:\\.|[^\s/"\'])*)+')
RELPATH_RX = re.compile(r'[^"\'\s]+(?:/[^"\'\s]*)*')
DQUOTE_RX = re.compile(r'"(?:\\.|[^"])*(?:"|$)')
QUOTE_RX = re.compile(r"'(?:\\.|[^'])*(?:'|$)")

class PathFinder(object):

    def __init__(self, absolute=False):
        self.state = State()
        self.reset("")
        self.absolute = absolute

    def reset(self, text):
        self.input = text
        self.length = len(text)
        self.pos = 0
        self.state.reset()
        self.paths = [""]
        self.quotes = 0
        self.dquotes = 0

    def search(self, text):
        self.reset(text)
        self.lex()
        return [p for p in self.paths if p]

    def lex(self):
        s = self.state
        while 1:
            pos = self.pos
            if pos >= self.length:
                break
            char = self.input[pos]
            if char is '\\':
                # antislash at last position
                if pos == self.length - 1:
                    if State.PATH in s:
                        self.paths[-1] += '\\'
                        break
                else:
                    pos += 2
            elif char is '/':
                s += State.PATH
                self.consume_path()
            elif char is '~':
                if State.PATH in s:
                    self.paths[-1] += char
                    self.pos += 1
                elif self.input[pos+1] is '/':
                    self.paths.append("~")
                    self.pos += 1
                    s += State.PATH
                    self.consume_path()
                else:
                    pos += 1
            elif char is '"':
                if State.PATH in s:
                    string = self.consume_quotes(char)
                    self.paths[-1] += string
                    continue
                if self.dquotes > 0:
                    self.dquotes -= 1
                    s -= State.DQUOTE
                else:
                    self.dquotes += 1
                    s += State.DQUOTE
                self.pos += 1
            elif char is "'":
                if State.PATH in s:
                    string = self.consume_quotes(char)
                    self.paths[-1] += string
                    continue
                if self.quotes > 0:
                    self.quotes -= 1
                    s -= State.QUOTE
                else:
                    self.quotes += 1
                    s += State.QUOTE
                self.pos += 1
            elif char is ' ':
                # state is in PATH and (QUOTE or DQUOTE)
                if State.PATH in s and (State.QUOTE in s or State.DQUOTE in s):
                    self.paths[-1] += char
                else:
                    self.paths.append("")
                    s -= State.PATH
                self.pos += 1
            else:
                rest = self.consume_relpath()
                if not rest:
                    self.pos += 1
                    continue
                if State.PATH in self.state:
                    self.paths[-1] += rest
                elif not self.absolute:
                    self.state += State.PATH
                    self.paths.append(rest)

    def consume_path(self):
        m = ABSPATH_RX.match(self.input, self.pos)
        if m:
            path = m.group(0)
            self.paths[-1] += path
            self.pos += len(path)
        else:
            self.pos += 1

    def consume_relpath(self):
        m = RELPATH_RX.match(self.input, self.pos)
        if m:
            res = m.group(0)
            self.pos += len(res)
            return res

    def consume_quotes(self, char):
        pattern = char is '"' and DQUOTE_RX or QUOTE_RX
        m = pattern.match(self.input, self.pos)
        text = m.group(0)
        text_l = len(text)
        self.pos += len(text)
        return text_l > 1 and text or ""

def test_finder(paths):
    finder = PathFinder(absolute=True)
    for path, expected in paths:
        result = finder.search(path)

def test_shlexer(paths):
    for path, expected in paths:
        tokens = shlexer(path)

start = time.clock()
for i in xrange(10000):
    test_finder(paths)
end = time.clock()
print "PathFinder: %s" % (end - start)

start = time.clock()
for i in xrange(10000):
    test_shlexer(paths)
end = time.clock()
print "Shlexer: %s" % (end - start)

#for path, expected in paths:
    #print "Searching:", path
    #finder = PathFinder(absolute=True)
    #result = finder.search(path)
    #try:
        #assert result == expected
    #except AssertionError, e:
        #print result, '!=', expected
