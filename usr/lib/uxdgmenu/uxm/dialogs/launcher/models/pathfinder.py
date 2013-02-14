import re

ABSPATH_RX = re.compile(r'(?:/(?:\\.|[^\s/"\'])*)+')
RELPATH_RX = re.compile(r'(?:\\.|[^"\'\s])+(?:/(?:\\.|[^"\'\s])*)*')
DQUOTE_RX = re.compile(r'"(?:\\.|[^"])*(?:"|$)')
QUOTE_RX = re.compile(r"'(?:\\.|[^'])*(?:'|$)")
WHITESPACE_RX = re.compile(r'\s+')


class State(object):
    """A bitmask class that stores the state of the path finder"""

    __slots__ = ('value')

    INITIAL = 0x0
    NONE = 0x1
    PATH = 0x2
    QUOTE = 0x4
    DQUOTE = 0x8

    def __init__(self):
        self.value = State.INITIAL

    def reset(self):
        self.value = State.INITIAL

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


class Token(object):

    __slots__ = ('_value', 'start', 'end', 'length', 'absolute')

    def __init__(self, value, start, absolute=False):
        self._value = value
        self.start = start
        self.length = len(value)
        self.end = self.start + self.length
        self.absolute = absolute

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        self._value = v
        l = len(v)
        self.length = l
        self.end = self.start + l

    def __getitem__(self, idx):
        return self._value[idx]

    def __len__(self):
        return self.length

    def __contains__(self, other):
        if isinstance(other, int):
            return self.start <= other <= self.end
        return str(other) in self._value

    def __add__(self, string):
        self._value += string
        l = len(string)
        self.length += l
        self.end += l
        return self

    def __eq__(self, other):
        if isinstance(other, Token):
            for attr in self.__slots__:
                if getattr(self, attr) != getattr(other, attr):
                    return False
            return True
        return self._value == other

    def __getattr__(self, attr):
        return getattr(self._value, attr)

    def __str__(self):
        return self._value

    def __repr__(self):
        return '<Token: %s, %s, %s, %s, %s>' % (
            self._value, self.start, self.end, self.length, self.absolute
        )


class PathFinder(object):
    """Extracts unix paths from strings"""

    def __init__(self, absolute=False):
        self.state = State()
        self.reset("")
        self.absolute = absolute

    def reset(self, text):
        self.input = text
        self.length = len(text)
        self.pos = 0
        self.state.reset()
        self.tokens = []

    def push_token(self, text, pos, absolute=False):
        self.tokens.append(Token(text, pos, absolute))
        #self.tokens.append([text, pos])

    def update_current_token(self, text):
        #self.tokens[-1][0] += text
        self.tokens[-1] += text

    def search(self, text):
        self.reset(text)
        self.lex()
        return self.tokens

    def lex(self):
        s = self.state
        l = self.length
        while 1:
            pos = self.pos
            if pos >= l:
                break
            in_path = State.PATH in s
            char = self.input[pos]
            if char is '\\':
                if in_path:
                    self.update_current_token(char)
                    self.pos += 1
                # antislash at last position
                elif pos == self.length - 1:
                    break
                else:
                    self.pos += 2
            elif char is '/':
                if not in_path:
                    self.push_token('', pos, True)
                s += State.PATH
                self.consume_path()
            elif char is '~':
                if in_path:
                    self.update_current_token(char)
                    self.pos += 1
                else:
                    self.push_token(char, pos, True)
                    self.pos += 1
                    s += State.PATH
                    self.consume_path()
            elif char is '"':
                if in_path:
                    string = self.consume_quotes(char)
                    self.update_current_token(string)
                    continue
                if State.DQUOTE in s:
                    s -= State.DQUOTE
                else:
                    s += State.DQUOTE
                self.pos += 1
            elif char is "'":
                if in_path:
                    string = self.consume_quotes(char)
                    self.update_current_token(string)
                    continue
                if State.QUOTE in s:
                    s -= State.QUOTE
                else:
                    s += State.QUOTE
                self.pos += 1
            elif char in ' \t\n\r\f\v':
                # state is in PATH and (QUOTE or DQUOTE)
                ws = self.consume_whitespace()
                if in_path and (State.QUOTE in s or State.DQUOTE in s):
                    self.update_current_token(ws)
                else:
                    s -= State.PATH
            else:
                rest = self.consume_relpath()
                if not rest:
                    self.pos += 1
                    continue
                if State.PATH in self.state:
                    self.update_current_token(rest)
                elif not self.absolute:
                    self.state += State.PATH
                    self.push_token(rest, pos)

    def consume_path(self):
        m = ABSPATH_RX.match(self.input, self.pos)
        if m:
            path = m.group(0)
            self.update_current_token(path)
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
        # if len(text) == 1, we found a quote at EOF
        return text_l > 1 and text or ""

    def consume_whitespace(self):
        m = WHITESPACE_RX.match(self.input, self.pos)
        if m:
            res = m.group(0)
            self.pos += len(res)
            return res


if __name__ == "__main__":
    paths = [
        # Escaped whitespace
        ('/bin/foo\ bar', [Token('/bin/foo\ bar', 0, True)]),
        # Escaped whitespace with trailing slash
        ('/bin/foo\ bar/', [Token('/bin/foo\ bar/', 0, True)]),
        # Escaped whitespace with trailing backslash
        ('/bin/foo\ bar/\\', [Token('/bin/foo\ bar/\\', 0, True)]),
        ('/bin/foo\ bar/\\ baz', [Token('/bin/foo\ bar/\\ baz', 0, True)]),
        # Escaped whitespace with trailing whitespace
        ('/bin/foo\ bar/\\ baz\\ ', [Token('/bin/foo\ bar/\\ baz\\ ', 0, True)]),
        # tilde
        ('cmd ~/.config/foo/bar.cfg', [Token('~/.config/foo/bar.cfg', 4, True)]),
        # Unescaped whitespace
        ('cmd ~/My Music/Stairway To Heaven.mp3', [Token('~/My', 4, True)]),
        # tilde and escaped whitespace
        ('cmd ~/Documents/Dossier\ de\ Presse.doc',
            [Token('~/Documents/Dossier\ de\ Presse.doc', 4, True)]),
        # path in double quotes
        ('cmd "/home/johndoe/new stuff"', [Token('/home/johndoe/new stuff', 5, True)]),
        # path in unterminated double quotes
        ('cmd "~/music/foo bar', [Token('~/music/foo bar', 5, True)]),
        # path containing double quotes
        ('cmd ~/music/Some\ "Album"', [Token('~/music/Some\ "Album"', 4, True)]),
        # path in single quotes containing double quotes
        ('cmd \'~/music/An "Album"\'', [Token('~/music/An "Album"', 5, True)]),
        # path in unterminated single quotes containing unterminated double quotes
        ('cmd \'~/music/An "Album', [Token('~/music/An "Album', 5, True)])
    ]

    finder = PathFinder(absolute=True)
    for path, expected in paths:
        result = finder.search(path)
        try:
            for i, r in enumerate(result):
                assert r == expected[i]
        except AssertionError, e:
            print "Error finding absolute paths in", path
            print ">>> got", result, ', expected', expected
    paths = [
        ('foo/bar\ baz/boo', [Token('foo/bar\ baz/boo', 0)]),
        ('vim src/foo\ bar/', [Token('vim', 0), Token('src/foo\ bar/', 4)]),
        ('diff src/foo\ bar/ "baba/wa ow"',
            [Token('diff', 0), Token('src/foo\ bar/', 5), Token('baba/wa ow', 20)]),
        ('diff src/foo\ bar/ ~',
            [Token('diff', 0), Token('src/foo\ bar/', 5), Token('~', 19, True)]),
        ('iceweasel http://duckduckgo.org/search?q=debian',
            [Token('iceweasel', 0), Token('http://duckduckgo.org/search?q=debian', 10)])
    ]
    finder = PathFinder(absolute=False)
    for path, expected in paths:
        result = finder.search(path)
        try:
            assert result == expected
        except AssertionError, e:
            print "Error finding relative paths in", path
            print ">>> got", result, ', expected', expected
