import os
import re
import pwd


def pgrep(pattern, **kwargs):
    return_name = False
    exact_match = False
    invert_match = False
    check_user = False
    check_cmdline = False
    if 'name' in kwargs:
        return_name = kwargs['name'] if kwargs['name'] is True else False
    if 'exact' in kwargs:
        exact_match = kwargs['exact'] if kwargs['exact'] is True else False
    if 'invert' in kwargs:
        invert_match = kwargs['invert'] if kwargs['invert'] is True else False
    if 'cmdline' in kwargs:
        check_cmdline = kwargs['cmdline'] if kwargs['cmdline'] is True else False
    if 'user' in kwargs:
        uid = pwd.getpwnam(kwargs['user']).pw_uid
        check_user = True
    if not exact_match:
        pattern = re.compile(pattern, re.I)
    matches = []
    append = matches.append

    pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
    for pid in pids:
        pid_dir = os.path.join('/proc', pid)
        pid_matches = False
        ret = [int(pid), None]
        if check_cmdline:
            cmdline_file = os.path.join(pid_dir, 'cmdline')
            if os.path.exists(cmdline_file):
                with open(cmdline_file, 'r') as f:
                    cmdline = f.read().strip()
                    if _pgrep_return_if_matches(pattern, cmdline, exact_match,
                                                invert_match):
                        pid_matches = True
        status_file = os.path.join(pid_dir, 'status')
        if os.path.exists(status_file):
            with open(status_file, 'r') as f:
                lines = f.readlines()
                if check_user:
                    data = lines[6].partition(':')[2].split()[0]
                    if int(data) != uid:
                        continue
                if return_name or not check_cmdline:
                    name = lines[0].partition(':')[2].strip()
                    if _pgrep_return_if_matches(pattern, name, exact_match,
                                                invert_match):
                        pid_matches = True
                        ret[1] = name
        if pid_matches:
            if return_name:
                append(tuple(ret))
            else:
                append(ret[0])
    return matches


def _pgrep_return_if_matches(pattern, subject, exact_match, invert_match):
    if exact_match:
        if invert_match:
            if pattern != subject:
                return True
        else:
            if pattern == subject:
                return True
    else:
        if invert_match:
            if not pattern.search(subject):
                return True
        else:
            if pattern.search(subject):
                return True
    return False
