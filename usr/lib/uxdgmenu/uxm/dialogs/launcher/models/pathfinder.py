import re

ABSPATH_RX = re.compile(r'(?:/(?:\\.|[^\s/"\'])*)+')
RELPATH_RX = re.compile(r'(?:\\.|[^"\'\s])+(?:/(?:\\.|[^"\'\s])*)*')
DQUOTE_RX = re.compile(r'"(?:\\.|[^"])*(?:"|$)')
QUOTE_RX = re.compile(r"'(?:\\.|[^'])*(?:'|$)")


class State(object):
    """A bitmask class that stores the state of the path finder"""

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
        self.paths = [""]
        self.tokens = [["", 0]]
        self.quotes = 0
        self.dquotes = 0

    def push_token(self, text, pos):
        self.tokens.append([text, pos])

    def update_token(self, text):
        self.tokens[-1][0] += text

    def search(self, text):
        self.reset(text)
        self.lex()
        return [t for t in self.tokens if t[0]]
        #return [p for p in self.paths if p]

    def lex(self):
        s = self.state
        l = self.length
        while 1:
            pos = self.pos
            if pos >= l:
                break
            char = self.input[pos]
            if char is '\\':
                print "got \\"
                if State.PATH in s:
                    self.paths[-1] += '\\'
                    self.update_token(char)
                    self.pos += 1
                # antislash at last position
                elif pos == self.length - 1:
                    break
                else:
                    self.pos += 2
            elif char is '/':
                s += State.PATH
                self.consume_path()
            elif char is '~':
                if State.PATH in s:
                    self.paths[-1] += char
                    self.update_token(char)
                    self.pos += 1
                else:
                    self.paths.append("~")
                    self.push_token(char, pos)
                    self.pos += 1
                    s += State.PATH
                    self.consume_path()
            elif char is '"':
                if State.PATH in s:
                    string = self.consume_quotes(char)
                    self.paths[-1] += string
                    self.update_token(string)
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
                    self.update_token(string)
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
                    self.update_token(char)
                else:
                    self.paths.append("")
                    self.push_token("", pos)
                    s -= State.PATH
                self.pos += 1
            else:
                rest = self.consume_relpath()
                if not self.absolute:
                    self.state += State.PATH
                if not rest:
                    self.pos += 1
                    continue
                if State.PATH in self.state:
                    self.paths[-1] += rest
                    self.update_token(rest)
                elif not self.absolute:
                    self.state += State.PATH
                    self.paths.append(rest)
                    self.push_token(rest, pos)

    def consume_path(self):
        m = ABSPATH_RX.match(self.input, self.pos)
        if m:
            path = m.group(0)
            self.paths[-1] += path
            self.update_token(path)
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


if __name__ == "__main__":
    paths = [
        # Escaped whitespace
        ('/bin/foo\ bar', ['/bin/foo\ bar']),
        # Escaped whitespace with trailing slash
        ('/bin/foo\ bar/', ['/bin/foo\ bar/']),
        # Escaped whitespace with trailing backslash
        ('/bin/foo\ bar/\\', ['/bin/foo\ bar/\\']),
        ('/bin/foo\ bar/\\ baz', ['/bin/foo\ bar/\\ baz']),
        # Escaped whitespace with trailing whitespace
        ('/bin/foo\ bar/\\ baz\\ ', ['/bin/foo\ bar/\\ baz\\ ']),
        # tilde
        ('cmd ~/.config/foo/bar.cfg', ['~/.config/foo/bar.cfg']),
        # Unescaped whitespace
        ('cmd ~/My Music/Stairway To Heaven.mp3', ['~/My']),
        # tilde and escaped whitespace
        ('cmd ~/Documents/Dossier\ de\ Presse.doc', ['~/Documents/Dossier\ de\ Presse.doc']),
        # path in double quotes
        ('cmd "/home/johndoe/new stuff"', ['/home/johndoe/new stuff']),
        # path in unterminated double quotes
        ('cmd "~/music/foo bar', ['~/music/foo bar']),
        # path containing double quotes
        ('cmd ~/music/Some\ "Album"', ['~/music/Some\ "Album"']),
        # path in single quotes containing double quotes
        ('cmd \'~/music/An "Album"\'', ['~/music/An "Album"']),
        # path in unterminated single quotes containing unterminated double quotes
        ('cmd \'~/music/An "Album', ['~/music/An "Album']),
    ]

    finder = PathFinder(absolute=True)
    for path, expected in paths:
        result = finder.search(path)
        try:
            assert result == expected
        except AssertionError, e:
            print "Error finding absolute paths in", path
            print ">>> got", result, ', expected', expected
    paths = [
        ('foo/bar\ baz/boo', ['foo/bar\ baz/boo']),
        ('vim src/foo\ bar/', ['vim', 'src/foo\ bar/']),
        ('diff src/foo\ bar/ "baba/wa ow"', ['diff', 'src/foo\ bar/', 'baba/wa ow']),
        ('diff src/foo\ bar/ ~', ['diff', 'src/foo\ bar/', '~']),
    ]
    finder = PathFinder(absolute=False)
    for path, expected in paths:
        result = finder.search(path)
        try:
            assert result == expected
        except AssertionError, e:
            print "Error finding relative paths in", path
            print ">>> got", result, ', expected', expected
