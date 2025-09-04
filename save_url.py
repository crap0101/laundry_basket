#!/usr/bin/env python

# Copyright (c) 2024-2025  Marco Chieppa | crap0101

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
import os
import random
import re
import sys
import time
from urllib.request import build_opener, URLError
# external:
from bs4 import BeautifulSoup
import magic
# https://github.com/crap0101/py_warnings
from py_warnings import pywarn

PROGNAME = 'save_url'
VERSION = '0.24'
LAST_UPDATE = '2025-09-04'

__doc__ = f'''==================================
{PROGNAME} v{VERSION} ({LAST_UPDATE})
Save an url to a file (or stdout).

Tested with Python 3.10.12
Requires: BeautifulSoup 4 => https://www.crummy.com/software/BeautifulSoup
          python-magic    => https://github.com/ahupp/python-magic
          py_warnings     => https://github.com/crap0101/py_warnings
==========================================================================
'''

PARSERS = ["html.parser", "html5lib", "lxml-xml", "lxml"]
RE_PATTERN = '[/:\\!]'
CHAR_REPLACEMENT = '_'
EXTENSIONS = ('.html', '.xml')
DATE_OPT = ('FN', 'FT')
DATE_METAVAR = 'STR'
DATE_HELP = f'''
Append a date to the output filename.
{DATE_METAVAR} can be:
"FN" to use the document's date found, or nothing if not found,
"FT" to use the document's date found or the date of the present day (YYYY-MM-DD) if not found,
Except these special values, any other value is considered as a custom date string to be used raw.
'''
DATE_SEPARATOR = '_'
DATE_PROPERTIES = ('article:modified_time', 'article:published_time', 'og:updated_time')
USER_AGENT_LIST = [
    ('User-agent', 'Mozilla/5.0'),
    ('User-agent','Chrome/Android: Mozilla/5.0 (Linux; Android 11) AppleWebKit/537.36'),
    ('User-agent','Firefox/Android: Mozilla/5.0 (Android 11; Mobile; rv:68.0) Gecko/68.0 Firefox/84.0'),
    ('User-agent','Chrome/Windows: Mozilla/5.0 (Windows NT 10.0; Win64; x64)'),
    ('User-agent','Chrome/Windows: Mozilla/5.0 (Windows NT 10.0) (KHTML, like Gecko) Chrome/87.0.4280.88'),
    ('User-agent','Chrome/macOS: Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1)'),
    ('User-agent','Chrome/Linux: Mozilla/5.0 (X11; Linux x86_64)'),
    ('User-agent','Chrome/iPhone: Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X)'),
    ('User-agent','Chrome/iPad: Mozilla/5.0 (iPad; CPU OS 14_3 like Mac OS X) AppleWebKit/605.1.15'),
    ('User-agent','Chrome/Android: Mozilla/5.0 (Linux; Android 10; SM-A205U)'),
    ('User-agent','Chrome/Android: Mozilla/5.0 (Linux; Android 10; LM-Q720)'),
    ('User-agent','Firefox/Windows: Mozilla/5.0 (Windows NT) Firefox/84.0'),
    ('User-agent','Firefox/macOS: Mozilla/5.0 (Macintosh; Intel Mac OS X 11.1) Gecko/20100101 Firefox/84.0'),
    ('User-agent','Firefox/Linux: Mozilla/5.0 (X11; Linux i686; rv:84.0) Firefox/84.0'),
    ('User-agent','Firefox/iPad: Mozilla/5.0 (iPad; CPU OS 11_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)'),
    ('User-agent','Chrome/Android: Mozilla/5.0 (Linux; Android 11) AppleWebKit/537.36'),
    ('User-agent','Firefox/Android: Mozilla/5.0 (Android 11; Mobile; rv:68.0) Gecko/68.0 Firefox/84.0')
]

class FakeBS:
    """
    A minimal fake BeautifulSoup() object, with just
    the needed attributes for this program.
    """
    def __init__ (self, data):
        self.data = data
        self.title = None
        self.is_xml = False
    def prettify (self):
        return self.data

def check_for_beauty (buff, size=2048) -> (bool, str):
    """
    Checks the filetype reading $size chars from $buff,
    returning True (and the data read) if can be managed by BeautifulSoup,
    False (and the data read) otherwise.
    """
    if not re.match('^(html|xml)',
                    magic.from_buffer(data := buff.read(size)),
                    re.I):
        return False, data
    return True, data


def find_date (data: [BeautifulSoup|FakeBS]) -> str:
    if isinstance(data, FakeBS):
        return ''
    where = True # "meta"
    for prop in DATE_PROPERTIES:
        if (p := data.find(where, property=prop)):
            # should be in ISO8601 format, keep only YYYY-MM-DD
            return p['content'][:10]
    return ''


def _get_date (date_opt, date_sep):
    if date_opt is None:
        f = lambda a: ''
        return f
    elif date_opt == DATE_OPT[0]:
        def __get_date_or_nothing (arg):
            s = find_date(arg)
            return s if not s else date_sep + s
        return __get_date_or_nothing
    elif date_opt == DATE_OPT[1]:
        def __get_date_or_now (arg):
            s = find_date(arg)
            return date_sep + s if s else date_sep + time.strftime("%Y-%m-%d")
        return __get_date_or_now
    else:
        cf = lambda a: date_sep + date_opt
        return cf


def get_data (opener, url, parser) -> (bool, [BeautifulSoup|FakeBS]):
    """
    Tries to read from $url using $opener and (for BeautifulSoup) $parser,
    returns a bool indicating success or failure
    and a BeautifulSoup or FakeBS object.
    """
    bs = result = False
    try:
        with opener.open(url) as f:
            ok, data = check_for_beauty(f)
            if ok:
                bs = BeautifulSoup(data + f.read(), parser)
            else:
                bs = FakeBS(data + f.read())
            result = True
    except URLError as err:
        bs = err
    return result, bs


def writefile (outfile, bs, encoding='utf-8') -> (bool, [int|Exception]):
    """
    Writes the $bs object (a BeautifulSoup or FakeBS instance) to $outfile
    with the give $encoding (default: utf-8).
    Returns a bool indicating success or failure and the amount
    of data written (or the exception raised trying).
    """
    try:
        with open(outfile, 'wb') as out:
            if isinstance(data := bs.prettify(), str):
                written = out.write(data.encode(encoding))
            else:
                written = out.write(data)                
            return True, written
    except PermissionError as err:
        return False, err


def doit (opener, url, dest, parser_name, regex, replacement, extension, datefunc):
    """
    Do the job.
    """
    ok, data = get_data(opener, url, parser_name)
    if not ok:
        pywarn.warn(pywarn.CustomWarning(f'ERROR with {url}: {data}'))
        return False
    if (title := data.title) is not None:
        data.title = regex.sub(replacement, title.get_text().strip())
    else:
        data.title = regex.sub(replacement, url.split('/')[-1].strip())
    if os.path.isdir(dest):
        data.title += datefunc(data)
        dest = os.path.join(dest, data.title)
        if extension is not None:
            dest += extension
        elif not isinstance(data, FakeBS):
            dest += EXTENSIONS[data.is_xml]
    ok, val = writefile(dest, data)
    if not ok:
        pywarn.warn(pywarn.CustomWarning(f'ERROR with {url}: {val}'))
        return False
    return True


def get_parser ():
    """Returns an argparse's parser object."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-d", "--append-date",
                        dest='date', default=None, metavar=DATE_METAVAR,
                        help=DATE_HELP)
    parser.add_argument('-D', '--date-separator',
                        dest='date_sep', default='_', metavar='STR',
                        help='''when appending the date to the filename, use %(metavar)s
                        as separator, default: "%(default)s"''')
    parser.add_argument("-e", "--extension",
                        dest="extension", default=None,  metavar="STR",
                        help='''Use STR as the output filename's extension,
                        defaults to guess it from the input data. Ignored if
                        the DEST argument is provided and is a regular file.
                        ''')
    parser.add_argument("-p", "--parser",
                        dest="default_parser", default=PARSERS[0],
                        choices=PARSERS, metavar="PARSER_NAME",
                        help='''Use this parser. Default: %(default)s.''')
    parser.add_argument("-r", "--replace-regex",
                        dest="replace_regex", default=RE_PATTERN,
                        metavar="REGEX",
                        help='''Replace chars in the input's title tag
                        which matches %(metavar)s. Default: %(default)s.
                        Use the empty string in both -r and -R options
                        to get the raw title.''')
    parser.add_argument("-R", "--replace-chars",
                        dest="replace_chars", default=CHAR_REPLACEMENT,
                        metavar="STR",
                        help='''Use %(metavar)s to replace chars matched by the
                        -r/--replace-regex option. Default: %(default)s.
                        Use the empty string in both -r and -R options
                        to get the raw title.''')                        
    """ #XXX not (yet) implemented
    parser.add_argument("-t", '--try-hard',
                        dest="try", action='store_true',
                        help='''If the specified parsed (or the default one)
                        returns error, tries with other available parses.''')
    """
    parser.add_argument("-u", "--user-agent",
                        dest="user_agent", metavar="STR",
                        help='''Use %(metavar)s as the user-agent. Defaults to
                        use a random one.''')
    parser.add_argument('-v', '--version',
                        action='version', version=f'{VERSION}')
    parser.add_argument("-W", "--warn-type",
                        dest='warn_type', default=pywarn.ALWAYS_WARNINGS,
                        choices=pywarn.WARN_OPT,
                        help='''Warning type: ignore it || send a message || raise an error.
                        Default: %(default)s.
                        Program's exit status is not affected by this option... If an error,
                        got an error.''')
    # positional:
    parser.add_argument('url',
                        metavar='URL',
                        help='''Retrieve %(metavar)s.''')
    parser.add_argument('dest',
                        nargs='?', default=None, metavar='DEST',
                        help='''Save on %(metavar)s. If a directory, uses by
                        default the input data's title tag for the filename.
                        If a path to a new regular file, use that ignoring
                        the value of the -d and -e options.
                        If not provided, write on stdout.''')
    return parser


if __name__ == '__main__':
    parser = get_parser()
    parsed = parser.parse_args()

    pywarn.set_showwarning(pywarn.bare_showwarning)
    pywarn.set_filter(parsed.warn_type, pywarn.CustomWarning)

    parsed.replace_regex = re.compile(parsed.replace_regex)
    if not parsed.dest:
        parsed.dest = sys.stdout.fileno()
    opener = build_opener()
    if parsed.user_agent:
        opener.addheaders = [('User-agent', parsed.user_agent)]
    else:
        opener.addheaders = [random.choice(USER_AGENT_LIST)]
    sys.exit(not doit(opener, parsed.url, parsed.dest, parsed.default_parser,
                      parsed.replace_regex, parsed.replace_chars,
                      parsed.extension, _get_date(parsed.date, parsed.date_sep)))
