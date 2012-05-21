#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2011  Marco Chieppa (aka crap0101)

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


import re
import os
import sys
import zipfile
from optparse import OptionParser
from xml.sax import parse
from xml.sax import handler

_VERSION = '0.6'
DESCRIPTION = "search patterns in Ooo Calc file"


def check_command_line ():
    parser = OptionParser(description=DESCRIPTION)
    parser.add_option("-r", "--regex", dest="regex",
                      help="Search using regular expression", metavar="RE")
    parser.add_option("-S", "--stringify", action="store_true", dest="stringify",
                      help="Search in the row as a string "
                      "(only with -r/--regex, ignored otherwise)")
    parser.add_option("-p", "--pattern", dest="pattern",
                      help="search PATTERN in the document", metavar="PATTERN")
    parser.add_option("-i", "--no-case", action="store_true", dest="no_case",
                      help="case insensitive search")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                      help="Verbose mode. Print some info about the jobs.")
    parser.add_option("-c", "--count", action="store_true", dest="count",
                      help="Report the number of items found")
    parser.add_option("-s", "--start", type="int", dest="start", metavar="NUM",
                      help="search PATTERN from the NUM column "
                      "(included, count starting from 0)")
    parser.add_option("-e", "--end", type="int", dest="end", metavar="NUM",
                      help="search PATTERN until the NUM column "
                      "(*not* included, count starting from 0)")
    parser.add_option('--version', dest='version', action='store_true')
    return parser


class RowCompare:
    _cmpfuncs = ('re', 'sre', 'sstr', 'istr')
    def __init__ (self, pattern, start=None, end=None):
        self.pattern = pattern
        self.start = start
        self.end = end

    def set_func (self, func_name):
        if func_name not in self._cmpfuncs:
            raise ValueError('no function named %s' % func_name)            
        setattr(self, 'search', getattr(self, func_name))

    def search(self, *args, **kword):
        return NotImplemented

    def re (self, to_match):
        return list(filter(self.pattern.match, to_match[self.start:self.end]))

    def sre (self, to_match):
        return self.pattern.match(str(to_match[self.start:self.end]))

    def sstr (self, to_match):
        return self.pattern in str(to_match[self.start:self.end])

    def istr (self, to_match):
        return self.pattern in str(to_match[self.start:self.end]).lower()


class Handler (handler.ContentHandler):

    def __init__(self):
        self.chars = [] 
        self.cells = []
        self.rows = []
        self.map_elements = {
            'table:table-cell': (self.startCell, self.addToCells),
            'table:table-row':(self.startRows, self.addToRows)}

    def DocumentLocator (self, locator):
        raise NotImplementedError

    def skippedEntity (self, name):
        print ("skipped entity %s" % name)

    def characters(self, char):
        self.chars.append(char)

    def startCell (self):
        self.chars = []

    def startRows (self):
        self.cells = []

    def addToCells (self):
        self.cells.append(''.join(self.chars))
        self.chars = []

    def addToRows (self):
        self.rows.append(self.cells)
        self.cells = []

    def startElement(self, name, attrs):
        try:
            self.map_elements[name][0]()
        except KeyError:
            pass

    def endElement(self, name):
        try:
            self.map_elements[name][1]()
        except KeyError:
            pass


class OOoSearch:
    def __init__ (self, compare, count=False, verbose=False):
        self.compare = compare
        self.count = count
        self.verbose = verbose
        
    def print_items(self, items, where):
        if self.verbose or self.count:
            filename = os.path.basename(where)
            print("* Searching in %s:" % filename)
        if self.count:
            total = len(list(items))
        for item in items:
            print(item)
        if self.count:
            print("* [%s] Found %d items" % (filename, total))

    def search(self, args):
        for arg in args:
            archive = zipfile.ZipFile(arg)
            table = Handler()
            parse(archive.open('content.xml'), table)
            self.print_items(filter(self.compare, table.rows), arg)
            archive.close()


if __name__ == '__main__':
    parser = check_command_line()
    options, args = parser.parse_args()
    if options.version:
        print(_VERSION)
        sys.exit(0)
    compare = None
    if options.regex and options.pattern:
        parser.error("options -r/--regex and -p/--pattern "
                     "are mutually exclusive")
    elif not any((options.regex, options.pattern)):
        parser.error("No pattern found")
    elif options.regex:
        if options.no_case:
            pattern = re.compile(options.regex, re.IGNORECASE)
        else:
            pattern = re.compile(options.regex)
        compare = RowCompare(pattern, options.start, options.end)
        if options.stringify:
            compare.set_func('sre')
        else:
            compare.set_func('re')
    else:
        pattern = options.pattern
        if options.no_case:
            compare = RowCompare(pattern.lower(), options.start, options.end)
            compare.set_func('istr')
        else:
            compare = RowCompare(options.pattern, options.start, options.end)
            compare.set_func('sstr')


    search = OOoSearch(compare.search, options.count, options.verbose)
    search.search(args)

