#!/usr/bin/env python

# Copyright (c) 2024  Marco Chieppa | crap0101

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
import re
import sys
from urllib.request import urlopen, URLError
# external:
from bs4 import BeautifulSoup

PROGNAME = 'save_url'
VERSION = '0.1'

__doc__ = f'''{PROGNAME} v{VERSION}
Save an url to a file (or stdout).

Tested with Python 3.10.12
Requires: BeautifulSoup 4 from https://www.crummy.com/software/BeautifulSoup/
'''

PARSERS = ["html.parser", "html5lib", "lxml-xml", "lxml"]
RE_PATTERN = '[/:\\!]'
CHAR_REPLACEMENT = '_'
EXTENSIONS = ('.html', '.xml')




def get_data(url, parser):
    bs = result = False
    try:
        with urlopen(url) as f:
            bs = BeautifulSoup(f, parser)
            result = True
    except URLError as err:
        bs = err
    return result, bs


def writefile(outfile, bsdata):
    try:
        with open(outfile, 'w') as out:
            written = out.write(bsdata.prettify())
            return True, written
    except PermissionError as err:
        return False, err


def doit(url, dest, parser_name, regex, replacement, extension):
    ok, data = get_data(url, parser_name)
    if not ok:
        print(data)
        return False
    if (title := data.title) is not None:
        data.title = regex.sub(replacement, title.get_text().strip())
    else:
        data.title = regex.sub(replacement, url.split('/')[-1].strip())
    if os.path.isdir(dest):
        dest = os.path.join(dest, data.title)
        if extension is not None:
            dest += extension
        else:
            dest += EXTENSIONS[data.is_xml]
    ok, val = writefile(dest, data)
    if not ok:
        print(val)
        return False
    return True


def get_parser():
    """Returns an argparse's parser object."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
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
    parser.add_argument('-v', '--version',
                        action='version', version=f'{VERSION}')
    # positional:
    parser.add_argument('url',
                        metavar='URL', help='''Retrieve %(metavar)s.''')
    parser.add_argument('dest',
                        nargs='?', default=None, metavar='DEST',
                        help='''Save on %(metavar)s. If a directory, uses by
                        default the input data's title tag for the filename.
                        If not provided, write on stdout.''')
    return parser

if __name__ == '__main__':
    parser = get_parser()
    parsed = parser.parse_args()
    
    parsed.replace_regex = re.compile(parsed.replace_regex)
    if not parsed.dest:
        parsed.dest = sys.stdout.fileno()
    sys.exit(not doit(parsed.url, parsed.dest, parsed.default_parser,
                      parsed.replace_regex, parsed.replace_chars,
                      parsed.extension))
