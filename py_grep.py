
# a stub... grep-like command

import argparse
import re
import sys

MATCHING_FUNCS = ('match', 'search')

def matching_lines (stream, pattern, flags=0, match_func="search"):
    is_match = getattr(re.compile(pattern, flags=flags), match_func)
    for elem in stream:
        if m := is_match(elem):
            yield m

class SetFlag(argparse.Action):
    def __init__(self, *a, **k):
        k['nargs'] = 0
        self._const_value = k['const']
        super().__init__(*a, **k)
    def __call__ (self, parser, namespace, value, option_string=None):
        setattr(namespace, 're_flags', getattr(namespace, 're_flags') | self._const_value)

def get_parser():
    parser = argparse.ArgumentParser(prog=sys.argv[0])
    parser.add_argument('-a', '--ascii-match',
                        dest='re_flags', action=SetFlag, default=0, const=re.A,
                        help="perform ASCII-only matching instead of full Unicode matching.")
    parser.add_argument('-i', '--ignore-case',
                        dest='re_flags', action=SetFlag, default=0, const=re.I,
                        help="Perform case-insensitive matching.")
    parser.add_argument('-m', '--multiline',
                        dest='re_flags', action=SetFlag, default=0, const=re.M)
    parser.add_argument('-M', '--matching-function',
                        dest='matching_func', choices=MATCHING_FUNCS, default='search')
    parser.add_argument('pattern')
    parser.add_argument('files', nargs='*')
    return parser


if __name__ == '__main__':
    parser = get_parser()
    parsed = parser.parse_args()
    if not parsed.files:
        parsed.files.append('-')
    for file in parsed.files:
        try:
            with (open(file) if file != '-' else sys.stdin) as f:
                for m in matching_lines(f, parsed.pattern, parsed.re_flags, parsed.matching_func):
                    print(m.string, end='')
        except (ValueError,PermissionError) as e:
            print(f"{parser.prog}: ERROR with file {file}: {e}", file=sys.stderr)
