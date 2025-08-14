
# a stub... grep-like command with some enhancem....cough cough... differences
# over the original.

# Copyright (c) 2025  Marco Chieppa | crap0101

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import argparse
from collections import deque, namedtuple
import itertools
import os
import re
import sys

# external package files_stuff @ https://github.com/crap0101/files_stuff
try:
    from files_stuff import filelist
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
searches read standard input.

Directories and recursive search needs the filelist module from then
files_stuff package @ https://github.com/crap0101/files_stuff.
'''

EPILOG='''EXIT STATUS
    Normally the exit status is 0 if a line is selected, 1 if no lines were
    selected, and 2 if an error occurred.
'''

Context = namedtuple('Context', ('pre','post'))


class FormatPrint:
    def __init__ (self, print_line=True, use_filename=False, use_line_num=False, zero_out=False, line_end=None):
        self._print_line = print_line
        self._use_filename = use_filename
        self._use_line_num = use_line_num
        self._zero_out = zero_out
        self.line_end = line_end
    def print_line (self, bool_value):
        self._print_line = bool(bool_value)
    def use_filename (self, bool_value):
        self._use_filename = bool(bool_value)
    def use_line_num (self, bool_value):
        self._use_line_num = bool(bool_value)
    def get_format (self):
        fmt = ''
        if self._print_line:
            fmt = '{line}'
        if self._use_line_num:
            fmt = '{}:{}'.format('{line_num}', fmt)
        if self._use_filename:
            fmt = '{}{}{}'.format('{filename}', ':' if not self._zero_out else '\0', fmt)
        return fmt

def file_with_match (stream, filename_or_label, matching_lines, matching_funcs, *others_not_used):
    for _ in matching_lines(stream, matching_funcs):
        yield {'filename':filename_or_label, 'line_num':0, 'line':''}
        break

def file_without_match (stream, filename_or_label, matching_lines, matching_funcs, *others_not_used):
    for _ in matching_lines(stream, matching_funcs):
        break
    else:
        yield {'filename':filename_or_label, 'line_num':0, 'line':''}
        
def standard_search (stream, filename_or_label, matching_lines, matching_funcs, max_count, context):
    for match_num, seq in enumerate(matching_lines(stream, matching_funcs, context), start=1):
        for (line_num, match) in seq:
            yield {'filename':filename_or_label, 'line_num':line_num, 'line':match}
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

def matching_lines_default (stream, match_funcs, *other_not_used):
    """line match"""
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

def matching_lines_context (stream, match_funcs, context):
    """line match with context"""
    # like sizedcontext.py module, that also in laundry basket.
    def check(funcs, elem):
        for f in funcs:
            if m := f(elem):
                return True, m
        return False, None
    preq = deque(maxlen=context.pre)
    post_ctx = 0
    for idx, elem in enumerate(stream, start=1):
        is_match, matches = check(match_funcs, elem)
        if is_match:
            for p in preq:
                yield [p]
            preq.clear()
            post_ctx = context.post
            if isinstance(matches, (re.Match, bool)):
                # for re.YYY functions and fixed_strings_match
                yield [[idx, elem]]
            else:
                # for finditer
                yield [[idx, m.group()] for m in matches]
        elif post_ctx:
            yield [[idx, elem]]
            post_ctx -= 1
        else:
            preq.append([idx, elem])

def negate_match(funcs):
    def inner_negate(line):
        return not any(f(line) for f in funcs)
    return inner_negate

def from_zero_lines_input(stream):
    for line in stream.read().split('\0'):
        yield line

def from_default_lines_input(stream):
    for line in stream:
        yield line.rstrip('\n')

'''
def findlist_func(match_obj):
    """Get a list instead of an iterator from re.finditer"""
    def inner_findlist(line):
        return list(match_obj.finditer(line))
    return inner_findlist
'''

# maybe excessive...
# class SetFlag(argparse.Action):
#     def __init__(self, *a, **k):
#         k['nargs'] = 0
#         self._const_value = k['const']
#         super().__init__(*a, **k)
#     def __call__ (self, parser, namespace, value, option_string=None):
#         setattr(namespace, 're_flags', getattr(namespace, 're_flags') | self._const_value)

def get_parser ():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     prog=PROGNAME, description=DESCRIPTION, epilog=EPILOG)
    matching = parser.add_argument_group('Matching Control')
    matching.add_argument('-a', '--ascii-match',
                        dest='re_flag_ascii', action='store_const', default=0, const=re.A,
                        help=r"""Make \w, \W, \b, \B, \d, \D, \s and \S Perform
                        ASCII-only matching instead of full Unicode matching.""")
    matching.add_argument('-e', '--regexp',
                        dest='extra_patterns', action='append', default=[], metavar=PATTERNS,
                        help='''Others patterns to be matched.
                        NOTE: any patterns which match makes the given line a matching line.''')
    matching.add_argument('-f', '--file',
                        dest='from_file', metavar='FILE',
                        help='''Obtain patterns from FILE, one per line.
                        Leading and trailing whitespaces are stripped from the patterns.''')
    matching.add_argument('-F', '--file-no-strip',
                        dest='from_file_no_strip', metavar='FILE',
                        help='Like -f but not strip leading and trailing whitespaces except the newlines.')
    matching.add_argument('-M', '--matching-function',
                        dest='matching_func', choices=MATCHING_FUNCS,
                        help='''Regex matching function (python's re.match or re.search).
                        See the python's documentation for the different
                        behaviour of these functions.
                        NOTE: ignored when using the --only-matching option.''')
    matching.add_argument('-i', '--ignore-case',
                        dest='re_flag_nocase', action='store_const', default=0, const=re.I,
                        help="Perform case-insensitive matching.")
    matching.add_argument('-S', '--fixed-strings',
                        dest='fixed_strings', action='store_true',
                        help=f'Interpret any {PATTERNS} as fixed strings, not regular expressions.')
    matching.add_argument('-v', '--invert-match',
                        dest='invert', action='store_true',
                        help='''Invert the sense of matching, to select non-matching lines.''')
    context_control = parser.add_argument_group('Context Control')
    context_control.add_argument('-A', '--after-context',
                                 dest='after_context', type=int, default=0,
                                 metavar='NUM', help='''
                                 Print %(metavar)s lines of trailing context after matching lines.
                                 NOTE: ignored when using the -o / --only-matching option.''')
    context_control.add_argument('-B', '--before-context',
                                 dest='before_context', type=int, default=0,
                                 metavar='NUM', help='''
                                 Print %(metavar)s lines of leading context before matching lines.
                                 NOTE: ignored when using the -o / --only-matching option.''')
    context_control.add_argument('-C', '--context',
                                 dest='context', type=int, default=0,
                                 metavar='NUM', help='''Print %(metavar)s lines of output context.
                                 NOTE: ignored when using the -o / --only-matching option.''')
    general_output = parser.add_argument_group('General Output Control')
    general_output.add_argument('-c', '--count',
                                dest='count', action='store_true',
                                help='''Suppress normal output; instead print a count of matching
                                lines for each input file. With the -v, --invert-match option
                                count non-matching lines.''')
    general_output.add_argument('-l', '--files-with-match',
                        dest='files_with_match', action='store_true',
                        help='''Suppress normal output; instead print the name of each
                        input file from which output would normally have been printed.
                        Scanning each input file stops upon first match.''')
    general_output.add_argument('-L', '--files-without-match',
                        dest='files_without_match', action='store_true',
                        help='''Suppress  normal  output; instead print the name of
                        each input file from which no output would normally have been printed.''')
    general_output.add_argument('-m', '--max-count',
                        dest='max_count', type=int, default=float('+inf'), metavar='NUM',
                        help='''Stop reading a file after %(metavar)s matching lines.
                        When the -v/--invert-match option is also used, stops after
                        outputting %(metavar)s non-matching lines.''')
    general_output.add_argument('-o', '--only-matching',
                        dest='only_matching', action='store_true',
                        help='''Print only the matched parts of a matching line,
                        with each such part on a separate output line. 
                        
                        NOTE: override the -M / --matching-function option. 
                        
                        NOTE: ignored when using -S / --fixed-strings. 
                        
                        NOTE: used together with --only-matching is not so meaningful
                        for the produced output, which results the same without this option.''')
    line_output = parser.add_argument_group('Output Line Control')
    line_output.add_argument('-n', '--line-number',
                        dest='line_number', action='store_true',
                        help='''Prefix each line of output with the 1-based line number
                        within its input file.''')
    line_output.add_argument('-H', '--with-filename',
                        dest='with_filename', action='store_true',
                        help='Print the file name for each match.')
    line_output.add_argument('--label', dest='label',
                             default=None, metavar='LABEL',
                             help='''Display input actually coming from standard input as input
                             coming from file %(metavar)s.''')
    line_output.add_argument('-Z', '--null',
                        dest='zero_out', action='store_true',
                        help='''Output a zero byte (the ASCII NUL character) instead of the
                        character that normally follows a file name.''')
    line_output.add_argument('-z', '--null-end',
                        dest='zero_end', action='store_true',
                        help='''Output a zero byte (the ASCII NUL character)
                        at the end of each output line.''')
    line_output.add_argument('-0', '--zero-input',
                        dest='zero_input', action='store_true',
                        help='''Treat input data as sequences of lines, each terminated
                        by a zero byte (the ASCII NUL character) instead of a newline.''')
    fd_selection = parser.add_argument_group('Files and Directories Selection')
    fd_selection.add_argument('-d', '--depth',
                        dest='depth', type=int, default=float('+inf'), metavar='NUM',
                        help='''When using the -r / --recursive option, descends %(metavar)s
                        levels from the given path (which is at level 0). Must be >= 0.
                        Default is a full recursive search.''')
    fd_selection.add_argument('-r', '--recursive',
                        dest='recursive', action='store_true',
                        help='''Read all files under each directory, recursively.
                        Note that if no file operand is given, %(prog)s searches
                        the working directory.''')
    parser.add_argument('pattern', metavar=PATTERNS,
                        help='''Default regex pattern to match.
                        To use the patterns provided with the -e or -F options only,
                        pass the empty string '' as the default pattern.''')
    parser.add_argument('files', nargs='*', metavar='FILE',
                        help='Files or directories to search in.')
    return parser


if __name__ == '__main__':
    __exit_status = 0
    parser = get_parser()
    parsed = parser.parse_args()
    if parsed.max_count == 0:
        sys.exit(1) # nothing to do...

    # conflicts:
    if parsed.max_count != -1 and (parsed.files_with_match or parsed.files_without_match):
        print(f'{parser.prog}: WARNING: --max-count ignored when'
              ' using --files-with-match or --files-without-match',
              file=sys.stderr)
    if parsed.only_matching and parsed.matching_func:
        print(f'{parser.prog}: WARNING: --matching-function ignored when'
              ' using --only-matching',
              file=sys.stderr)
    if parsed.only_matching and (parsed.files_with_match or parsed.files_without_match):
        print(f'{parser.prog}: WARNING: --only-matching ignored when'
              ' using --files-with-match or --files-without-match',
              file=sys.stderr)
    if parsed.only_matching and parsed.fixed_strings:
        print(f'{parser.prog}: WARNING: --only-matching ignored when'
              ' using --fixed-strings', file=sys.stderr)
    if parsed.only_matching and any([parsed.context, parsed.after_context, parsed.before_context]):
        print(f'{parser.prog}: WARNING: /--(after-|before-)?context/ ignored when'
              ' using --only-matching', file=sys.stderr)
    if any([parsed.before_context, parsed.after_context]) and parsed.context:
        parser.error('conflicting context controls: --(after|before) and --context')
    if parsed.count and (parsed.files_with_match or parsed.files_without_match):
        print(f'{parser.prog}: WARNING: --count ignored when'
              ' using --files-with-match or --files-without-match!',
              file=sys.stderr)
    if parsed.count and parsed.line_number:
        print(f'{parser.prog}: WARNING: --line-number ignored when'
              ' using --count!',
              file=sys.stderr)

    # output formatting:
    if (parsed.files_with_match or parsed.files_without_match):
        format_print = FormatPrint(False, parsed.with_filename, False, parsed.zero_out)
    else:
        format_print = FormatPrint(True, parsed.with_filename, parsed.line_number, parsed.zero_out)
    if parsed.zero_end:
        format_print.line_end = '\0'

    # recursive level check:
    if parsed.depth < 0:
        parser.error("depth must be >= 0")

    # input files:
    if not parsed.files:
        if parsed.recursive:
            if not CAN_SCANDIR:
                parser.error('Missing module: filelist')
            parsed.files = [filelist.find(os.getcwd(), parsed.depth)]
        else:
             parsed.files.append(['-'])
    else:
        if parsed.recursive:
            if not CAN_SCANDIR:
                parser.error('Missing module: filelist')
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
            parsed.files = [parsed.files]

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
            parsed.matching_func = 'findall' #XXXX# using findlist_func
            __patterns = ['|'.join(__patterns)]
        elif not parsed.matching_func:
            parsed.matching_func = 'search'
        for p in __patterns:
            #if parsed.only_matching:
            #    __matching_funcs.append(findlist_(re.compile(p, flags=__flags))) #findlist_func(re.compile(p, flags=__flags)))
            #else:
            __matching_funcs.append(getattr(re.compile(p, flags=__flags), parsed.matching_func))
    # ...
    if parsed.invert:
        __matching_funcs = [negate_match(__matching_funcs)]
    # context
    if any([parsed.context, parsed.after_context, parsed.before_context]):
        if parsed.only_matching:
            __context = Context(0, 0)
            matching_lines = matching_lines_default
        if parsed.context: # this or the others, checked before in the "# conflict" section
            __context = Context(parsed.context, parsed.context)
            matching_lines = matching_lines_context
        else:
            __context = Context(parsed.before_context, parsed.after_context)
            matching_lines = matching_lines_context
    else:
        __context = Context(0, 0)
        matching_lines = matching_lines_default

    # do it:
    __got_match = 0
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
                _format = format_print.get_format()
            if parsed.zero_input:
                split_lines = from_zero_lines_input
            else:
                split_lines = from_default_lines_input
            with (open(infile) if infile != '-' else sys.stdin) as stream:
                __label = infile if (infile != '-' or parsed.label is None) else parsed.label
                if parsed.count and not (parsed.files_with_match or parsed.files_without_match):
                    __got_match = sum(1 for _ in _f(split_lines(stream),
                                                    __label, matching_lines,
                                                    __matching_funcs, parsed.max_count,
                                                    __context))
                    print(((infile + ('\0' if parsed.zero_out else '') +  ':')
                           if parsed.with_filename else '')
                          + str(__got_match),
                          end=format_print.line_end)
                else:
                    for __got_match, res in enumerate(
                            _f(split_lines(stream),
                               __label, matching_lines,
                               __matching_funcs, parsed.max_count,
                               __context),
                            start=1):
                        print(_format.format(**res), end=format_print.line_end)
                if not __got_match:
                    __exit_status = 1
        except (ValueError, PermissionError, FileNotFoundError) as e:
            print(f"{parser.prog}: ERROR with file {infile}: {e}", file=sys.stderr)
            __exit_status = 2
    sys.exit(__exit_status)

