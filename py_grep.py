
# a stub... grep-like command

import argparse
import re
import sys

MATCHING_FUNCS = ('match', 'search')
PATTERN = 'PATTERN'

def fixed_string_match (pattern):
    def match_line (line):
        return pattern in line
    return match_line

def matching_lines (stream, match_funcs):
    for idx, elem in enumerate(stream, start=1):
        for f in match_funcs:
            if m := f(elem):
                yield idx, elem
                break

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
                        help="Perform ASCII-only matching instead of full Unicode matching.")
    parser.add_argument('-e', '--regexp',
                        dest='extra_patterns', action='append', default=[], metavar=PATTERN,
                        help='''Others patterns to be matched.
                        NOTE: any patterns which match makes the given line a matching line.''')
    parser.add_argument('-F', '--fixed-strings',
                        dest='fixed_strings', action='store_true',
                        help=f'Interpret any {PATTERN} as fixed strings, not regular expressions.')
    parser.add_argument('-i', '--ignore-case',
                        dest='re_flags', action=SetFlag, default=0, const=re.I,
                        help="Perform case-insensitive matching.")
    # line-oriented, not used:
    #parser.add_argument('-m', '--multiline',
    #                    dest='re_flags', action=SetFlag, default=0, const=re.M)
    parser.add_argument('-M', '--matching-function',
                        dest='matching_func', choices=MATCHING_FUNCS, default='search',
                        help='''Regex matching function (python's re.match or re.search).''')
    parser.add_argument('-m', '--max-count',
                        dest='max_count', type=int, default=-1, metavar='NUM',
                        help='''Stop reading a file after %(metavar)s matching lines.
                        When the -v/--invert-match option is also used, stops after
                        outputting %(metavar)s non-matching lines.''')
    parser.add_argument('-n', '--line-number',
                        dest='line_number', action='store_true',
                        help='''Prefix each line of output with the 1-based line number
                        within its input file.''')
    parser.add_argument('-v', '--invert-match',
                        dest='invert', action='store_true',
                        help='''Invert the sense of matching, to select non-matching lines.
                        NOTE: works when there's one pattern only present at command line.''')
    parser.add_argument('pattern', metavar=PATTERN, help='regex pattern to match')
    parser.add_argument('files', nargs='*')
    return parser


if __name__ == '__main__':
    __errors = 0
    parser = get_parser()
    parsed = parser.parse_args()
    if parsed.line_number:
        __print = lambda n, l, e: print(f'{n}:{l}', end=e)
    else:
        __print = lambda n, l, e: print(l, end=e)
    if not parsed.files:
        parsed.files.append('-')
    __patterns = parsed.extra_patterns
    __patterns.append(parsed.pattern)
    __matching_funcs = []
    if parsed.fixed_strings:
        for p in __patterns:
            __matching_funcs.append(fixed_string_match(p))
    else:
        for p in __patterns:
            __matching_funcs.append(getattr(re.compile(p, flags=parsed.re_flags), parsed.matching_func))
    if parsed.invert:
        __matching_funcs = [lambda arg: not f(arg) for f in __matching_funcs]
    for file in parsed.files:
        try:
            with (open(file) if file != '-' else sys.stdin) as f:
                for match_num, (line_num, m) in enumerate(matching_lines(f, __matching_funcs), start=1):
                    __print(line_num, m, '')
                    if match_num == parsed.max_count:
                        break
        except (ValueError, PermissionError, FileNotFoundError) as e:
            print(f"{parser.prog}: ERROR with file {file}: {e}", file=sys.stderr)
            __errors += 1
    sys.exit(__errors)
