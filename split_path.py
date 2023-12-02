#coding: utf-8
#
# author: Marco Chieppa | crap0101
#

from os.path import split as _split
from os import sep as _sep

def split_path (path):
    head, tail = _split(path)
    if head in ('', _sep, path):
        yield head + tail
    else:
#        yield from split_path(head)
        for c in split_path(head):
            yield c
        if tail:
            yield tail

def test (lst):
    from os.path import join as _join
    from re import sub as _s
    for arg in lst:
        joined = _join(*split_path(arg))
        assert _s('/$', '', arg) == _s('/$', '', joined), (arg, joined)
    print('ok')


if __name__ == '__main__':
    import sys
    if '-t' in sys.argv:
        sys.argv.remove('-t')
        test(sys.argv[1:])
    else:
        for arg in sys.argv[1:]:
            print(list(split_path(arg)))
