import re

_find_unsafe_chars = re.compile(r'[^\w@%+=:,./-]').search
EXE_REGEX = re.compile(r' (\s*["\'])?(?:\s*%[a-zA-Z])+\1?')


def quote(s):
    """Return a shell-escaped version of the string *s*."""
    if not s:
        return "''"
    if _find_unsafe_chars(s) is None:
        return s

    # use single quotes, and put single quotes into double quotes
    # the string $'b is then quoted as '$'"'"'b'
    return "'" + s.replace("'", "'\"'\"'") + "'"


def clean_exec(cmd):
    """Cleans commands found in Desktop entries"""
    #clean = []
    #for arg in shlex.split(cmd):
        #if '%' == arg[0]:
            #continue
        #clean.append(arg)
    #return ' '.join(clean)
    return EXE_REGEX.sub('', cmd)
