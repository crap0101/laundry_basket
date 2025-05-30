
# a stub... grep-like command with some enhancem....cough cough... differences
# over the original.

import argparse
import re
import sys

MATCHING_FUNCS = ('match', 'search')
PATTERNS = 'PATTERNS'
DESCRIPTION = '''Searches for PATTERNS in each FILE.
PATTERNS is one or more patterns separated by newline characters,
and py_grep prints each line that matches a pattern.'''

class FormatPrint:
    def __init__(self, use_filename=False, use_line_num=False):
        self._use_filename = use_filename
        self._use_line_num = use_line_num
    def use_filename(self, bool_value):
        self._use_filename = bool(bool_value)
    def use_line_num(self, bool_value):
        self._use_line_num = bool(bool_value)
    def get_format(self):
        fmt = '{line}'
        if self._use_line_num:
            fmt = '{line_num}:' + fmt
        if self._use_filename:
            fmt = '{filename}:' + fmt
        return fmt

def file_with_match(infile, matching_funcs, *others):
    with (open(infile) if infile != '-' else sys.stdin) as f:
        for _ in matching_lines(f, matching_funcs):
            yield {'filename':infile, 'line_num':0, 'line':''}
            break

def file_without_match(infile, matching_funcs, *others):
    with (open(infile) if infile != '-' else sys.stdin) as f:
        for _ in matching_lines(f, matching_funcs):
            break
        else:
            yield {'filename':infile, 'line_num':0, 'line':''}
        
def standard_search (infile, matching_funcs, max_count):#, format_print):
    with (open(infile) if infile != '-' else sys.stdin) as f:
        #_format = format_print.get_format()
        for match_num, (line_num, m) in enumerate(matching_lines(f, matching_funcs), start=1):
            yield {'filename':infile, 'line_num':line_num, 'line':m}
            #print(_format.format(filename=infile, line_num=line_num, line=m), end='')
            if match_num == max_count:
                break

def pattern_from_file (path, strip=True):
    with open(path) as f:
        if strip:
            return list(line.strip() for line in f)
        return list(f.read().splitlines())

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

# maybe excessive...
# class SetFlag(argparse.Action):
#     def __init__(self, *a, **k):
#         k['nargs'] = 0
#         self._const_value = k['const']
#         super().__init__(*a, **k)
#     def __call__ (self, parser, namespace, value, option_string=None):
#         setattr(namespace, 're_flags', getattr(namespace, 're_flags') | self._const_value)

def get_parser():
    parser = argparse.ArgumentParser(prog=sys.argv[0], description=DESCRIPTION)
    parser.add_argument('-a', '--ascii-match',
                        dest='re_flag_ascii', action='store_const', default=0, const=re.A,
                        help=r"""Make \w, \W, \b, \B, \d, \D, \s and \S Perform
                        ASCII-only matching instead of full Unicode matching.""")
    parser.add_argument('-c', '--count',
                        dest='count', action='store_true')
    parser.add_argument('-e', '--regexp',
                        dest='extra_patterns', action='append', default=[], metavar=PATTERNS,
                        help='''Others patterns to be matched.
                        NOTE: any patterns which match makes the given line a matching line.''')
    parser.add_argument('-f', '--file',
                        dest='from_file', metavar='FILE',
                        help='''Obtain patterns from FILE, one per line.
                        Leading and trailing whitespaces are stripped from the patterns.''')
    parser.add_argument('-F', '--file-no-strip',
                        dest='from_file_no_strip', metavar='FILE',
                        help='Like -f but not strip leading and trailing whitespaces except the newlines.')
    parser.add_argument('-H', '--with-filename',
                        dest='with_filename', action='store_true',
                        help='Print the file name for each match.')
    parser.add_argument('-i', '--ignore-case',
                        dest='re_flag_nocase', action='store_const', default=0, const=re.I,
                        help="Perform case-insensitive matching.")
    parser.add_argument('-l', '--files-with-match',
                        dest='files_with_match', action='store_true',
                        help='''Suppress normal output; instead print the name of each
                        input file from which output would normally have been printed.
                        Scanning each input file stops upon first match.''')
    parser.add_argument('-L', '--files-without-match',
                        dest='files_without_match', action='store_true',
                        help='''Suppress  normal  output; instead print the name of
                        each input file from which no output would normally have been printed.''')
    parser.add_argument('-M', '--matching-function',
                        dest='matching_func', choices=MATCHING_FUNCS, default='search',
                        help='''Regex matching function (python's re.match or re.search).
                        See the python's documentation for the different
                        behaviour of these functions.''')
    parser.add_argument('-m', '--max-count',
                        dest='max_count', type=int, default=-1, metavar='NUM',
                        help='''Stop reading a file after %(metavar)s matching lines.
                        When the -v/--invert-match option is also used, stops after
                        outputting %(metavar)s non-matching lines.''')
    parser.add_argument('-n', '--line-number',
                        dest='line_number', action='store_true',
                        help='''Prefix each line of output with the 1-based line number
                        within its input file.''')
    parser.add_argument('-S', '--fixed-strings',
                        dest='fixed_strings', action='store_true',
                        help=f'Interpret any {PATTERNS} as fixed strings, not regular expressions.')
    parser.add_argument('-v', '--invert-match',
                        dest='invert', action='store_true',
                        help='''Invert the sense of matching, to select non-matching lines.
                        NOTE: works when there's one pattern only present at command line.''')
    parser.add_argument('pattern', metavar=PATTERNS,
                        help='''Default regex pattern to match.
                        To use the patterns provided with the -e or -F options only,
                        pass the empty string '' as the default pattern.''')
    parser.add_argument('files', nargs='*', metavar='FILE')
    return parser


if __name__ == '__main__':
    __errors = 0
    parser = get_parser()
    parsed = parser.parse_args()
    #conflicts:
    if parsed.max_count != -1 and (parsed.files_with_match or parsed.files_without_match):
        print(f'{parser.prog}: WARNING: "--max-count" ignored when'
              ' using "--files-with-match" or "--files-without-match"!',
              file=sys.stderr)
    if parsed.count and (parsed.files_with_match or parsed.files_without_match):
        print(f'{parser.prog}: WARNING: "--count" ignored when'
              ' using "--files-with-match" or "--files-without-match"!',
              file=sys.stderr)
    if parsed.count and parsed.line_number:
        print(f'{parser.prog}: WARNING: "--line-number" ignored when'
              ' using "--count"!',
              file=sys.stderr)
    # output formatting:
    format_print = FormatPrint()
    format_print.use_line_num(parsed.line_number)
    format_print.use_filename(parsed.with_filename)
    # input files:
    if not parsed.files:
        parsed.files.append('-')
    # patterns to match:
    __patterns = []
    for p in parsed.extra_patterns:
        __patterns.extend(p.splitlines())
    if parsed.pattern:
        __patterns.extend(parsed.pattern.splitlines())
    if parsed.from_file:
        try:
            __patterns.extend(pattern_from_file(parsed.from_file, True))
        except OSError as e:
            parser.error(e)
    if parsed.from_file_no_strip:
        try:
            __patterns.extend(pattern_from_file(parsed.from_file_no_strip, False))
        except OSError as e:
            parser.error(e)
    if not __patterns:
        parser.error("No pattern specified!")
    # string/regex matching functions:
    __matching_funcs = []
    if parsed.fixed_strings:
        for p in __patterns:
            __matching_funcs.append(fixed_string_match(p))
    else:
        __flags = parsed.re_flag_ascii | parsed.re_flag_nocase
        for p in __patterns:
            __matching_funcs.append(getattr(re.compile(p, flags=__flags), parsed.matching_func))
    # ...
    if parsed.invert:
        __matching_funcs = [lambda arg: not f(arg) for f in __matching_funcs]
    # do it:
    for infile in parsed.files:
        try:
            if parsed.files_with_match:
                _end = '\n'
                _format = '{filename}'
                _f = file_with_match
            elif parsed.files_without_match:
                _f = file_without_match
                _end = '\n'
                _format = '{filename}'
            else:
                _f = standard_search
                _end = ''
                _format = format_print.get_format()
            if parsed.count and not (parsed.files_with_match or parsed.files_without_match):
                print(((infile + ':') if parsed.with_filename else '')
                      + str(sum(1 for _ in _f(infile, __matching_funcs, parsed.max_count))))
            else:
                for res in _f(infile, __matching_funcs, parsed.max_count):
                    print(_format.format(**res), end=_end)
        except (ValueError, PermissionError, FileNotFoundError) as e:
            print(f"{parser.prog}: ERROR with file {infile}: {e}", file=sys.stderr)
            __errors += 1
    sys.exit(__errors)

