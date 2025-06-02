
# Author: Marco Chieppa
# 2025
# a stub... grep-like command with some enhancem....cough cough... differences
# over the original.

import argparse
import itertools
import os
import re
import sys

# optional module filelist.py (this too from the laundry basket)
try:
    import filelist
    CAN_SCANDIR = True
except ImportError:
    CAN_SCANDIR = False

MATCHING_FUNCS = ('match', 'search')
PROGNAME = 'py_grep'
PATTERNS = 'PATTERNS'
DESCRIPTION = '''Searches for PATTERNS in each FILE.
PATTERNS is one or more patterns separated by newline characters,
and %(prog)s prints each line that matches a pattern.

A FILE of "-" stands for standard input. If no FILE is given,
recursive searches examine the working directory, and nonrecursive
searches read standard input.'''

class FormatPrint:
    def __init__(self, use_filename=False, use_line_num=False, zero_out=False, line_end=None):
        self._use_filename = use_filename
        self._use_line_num = use_line_num
        self._zero_out = zero_out
        self.line_end = line_end
    def use_filename(self, bool_value):
        self._use_filename = bool(bool_value)
    def use_line_num(self, bool_value):
        self._use_line_num = bool(bool_value)
    def get_format(self):
        fmt = '{line}'
        if self._use_line_num:
            fmt = '{}:{}'.format('{line_num}', fmt)
        if self._use_filename:
            fmt = '{}{}:{}'.format('{filename}', '' if not self._zero_out else '\0', fmt)
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
        
def standard_search (infile, matching_funcs, max_count):
    with (open(infile) if infile != '-' else sys.stdin) as f:
        for match_num, seq in enumerate(matching_lines(f, matching_funcs), start=1):
            for (line_num, match) in seq:
                yield {'filename':infile, 'line_num':line_num, 'line':match}
            if match_num >= max_count:
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
    """regex match"""
    for idx, elem in enumerate(stream, start=1):
        for f in match_funcs:
            if matches := f(elem):
                if isinstance(matches, (re.Match, bool)):
                    # for re.YYY functions and fixed_strings_match
                    yield [[idx, elem]]
                else:
                    # for finditer
                    yield [[idx, m.group()] for m in matches]
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
    parser = argparse.ArgumentParser(prog=PROGNAME, description=DESCRIPTION)
    parser.add_argument('-a', '--ascii-match',
                        dest='re_flag_ascii', action='store_const', default=0, const=re.A,
                        help=r"""Make \w, \W, \b, \B, \d, \D, \s and \S Perform
                        ASCII-only matching instead of full Unicode matching.""")
    parser.add_argument('-c', '--count',
                        dest='count', action='store_true')
    parser.add_argument('-d', '--depth',
                        dest='depth', type=int, default=float('+inf'), metavar='NUM',
                        help='''When using the -r / --recursive option, descends %(metavar)s
                        levels from the given path (which is at level 0). Must be >= 0.
                        Default is a full recursive search.''')
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
    parser.add_argument('-o', '--only-matching',
                        dest='only_matching', action='store_true',
                        help='''Print only the matched (non-empty) parts of a matching line,
                        with each such part on a separate output line.
                        NOTE: override the "-M / --matching-function" option.
                        NOTE: ignored when using "-S / --fixed-strings"''')
    parser.add_argument('-r', '--recursive',
                        dest='recursive', action='store_true',
                        help='''Read all files under each directory, recursively.
                        Note that if no file operand is given, %(prog)s searches
                        the working directory.''')
    parser.add_argument('-S', '--fixed-strings',
                        dest='fixed_strings', action='store_true',
                        help=f'Interpret any {PATTERNS} as fixed strings, not regular expressions.')
    parser.add_argument('-v', '--invert-match',
                        dest='invert', action='store_true',
                        help='''Invert the sense of matching, to select non-matching lines.
                        NOTE: works when there's one pattern only present at command line.''')
    parser.add_argument('-Z', '--null',
                        dest='zero_out', action='store_true',
                        help='''Output a zero byte (the ASCII NUL character) instead of the
                        character that normally follows a file name.''')
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
    if parsed.max_count == 0:
        sys.exit(0) # nothing to do...
    #conflicts:
    if parsed.max_count != -1 and (parsed.files_with_match or parsed.files_without_match):
        print(f'{parser.prog}: WARNING: "--max-count" ignored when'
              ' using "--files-with-match" or "--files-without-match"!',
              file=sys.stderr)
    if parsed.only_matching and (parsed.files_with_match or parsed.files_without_match):
        print(f'{parser.prog}: WARNING: "--only-matching" ignored when'
              ' using "--files-with-match" or "--files-without-match"!',
              file=sys.stderr)
    if parsed.only_matching and parsed.fixed_strings:
        print(f'{parser.prog}: WARNING: "--only-matching" ignored when'
              ' using "--fixed-strings"!', file=sys.stderr)
    if parsed.count and (parsed.files_with_match or parsed.files_without_match):
        print(f'{parser.prog}: WARNING: "--count" ignored when'
              ' using "--files-with-match" or "--files-without-match"!',
              file=sys.stderr)
    if parsed.count and parsed.line_number:
        print(f'{parser.prog}: WARNING: "--line-number" ignored when'
              ' using "--count"!',
              file=sys.stderr)
    # output formatting:
    format_print = FormatPrint(parsed.with_filename, parsed.line_number, parsed.zero_out)
    # recursive level check:
    if parsed.depth < 0:
        parser.error("depth must be > 0")
    # input files:
    if not parsed.files:
        if parsed.recursive:
            parsed.files = [filelist.find(os.getcwd(), parsed.depth)]
        else:
             parsed.files.append(['-'])
    else:
        if parsed.recursive:
            flst = []
            for p in parsed.files:
                if os.path.isdir(p):
                    flst.append(filelist.find(p, parsed.depth))
                elif os.path.isfile(p):
                    flst.append([p])
                else:
                    parser.error('Unknown input: {}'.format(p))
            parsed.files = flst
        else:
            for p in parsed.files:
                if os.path.isdir(p):
                    parser.error('Is a directory: {}'.format(p))

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
        if parsed.only_matching:
            parsed.matching_func = 'finditer'
        for p in __patterns:
            __matching_funcs.append(getattr(re.compile(p, flags=__flags), parsed.matching_func))
    # ...
    if parsed.invert:
        __matching_funcs = [lambda arg: not f(arg) for f in __matching_funcs]
    # do it:
    for infile in itertools.chain(*parsed.files):
        try:
            if parsed.files_with_match:
                _format = '{filename}'
                _f = file_with_match
            elif parsed.files_without_match:
                _f = file_without_match
                _format = '{filename}'
            else:
                _f = standard_search
                if (not parsed.only_matching) or parsed.fixed_strings:
                    format_print.line_end = ''
                _format = format_print.get_format()
            if parsed.count and not (parsed.files_with_match or parsed.files_without_match):
                print(((infile + ('\0' if parsed.zero_out else '') +  ':')
                       if parsed.with_filename else '')
                      + str(sum(1 for _ in _f(infile, __matching_funcs, parsed.max_count))))
            else:
                for res in _f(infile, __matching_funcs, parsed.max_count):
                    print(_format.format(**res), end=format_print.line_end)
        except (ValueError, PermissionError, FileNotFoundError) as e:
            print(f"{parser.prog}: ERROR with file {infile}: {e}", file=sys.stderr)
            __errors += 1
    sys.exit(__errors)

