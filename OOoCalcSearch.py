#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2011-2026  Marco Chieppa (aka crap0101)

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
import io
import os
import re
import sys
from xml.sax import parse
from xml.sax import handler
import zipfile
from optparse import OptionParser

_VERSION = '0.7'
DESCRIPTION = "search patterns in Ooo Calc files"

def check_command_line ():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("-c", "--count",
                        action="store_true", dest="count",
                        help="Also report the number of items found")
    parser.add_argument("-v", "--verbose",
                        action="store_true", dest="verbose",
                        help="Verbose mode. Print some info about the jobs")
    parser.add_argument('--version', action='version', version=f'%(prog)s {_VERSION}')
    parser.add_argument('pattern', metavar='PATTERN', help='search for the %(metavar)s pattern')
    parser.add_argument('files', metavar='FILE', nargs='*', default=[sys.stdin], help='search in the given %(metavar)s, default: stdin')

    filtering = parser.add_argument_group('filtering')
    filtering.add_argument("-s", "--start",
                           type=int, dest="start", metavar="NUM",
                           help="search PATTERN from the NUM column "
                           "(included, counting from 0)")
    filtering.add_argument("-e", "--end",
                           type=int, dest="end", metavar="NUM",
                           help="search PATTERN until the NUM column "
                           "(*not* included, counting from 0)")

    searching = parser.add_argument_group('searching')
    searching.add_argument("-i", "--no-case",
                           action="store_const", const=re.IGNORECASE, default=0, dest="case",
                           help="case insensitive search")
    searching.add_argument("-S", "--stringify",
                           action="store_const", const='sre', default='re', dest="stringify",
                           help="Search in the given columns as a single string")
    patterns = searching.add_mutually_exclusive_group()
    patterns.add_argument("-r", "--regex",
                          dest="regex", action='store_true',
                          help="Search using regular expression")
    return parser


class Finder:
    _cmpfuncs = ('re', 'sre')
    _findfuncs = ('match', 'search')
    def __init__ (self, pattern, start=None, end=None):
        self.pattern = pattern
        self.start = start
        self.end = end
        self.search = lambda p: self.re(p)
        self.find = self.pattern.match

    def set_findfunc (self, func_name):
        if func_name not in self._findfuncs:
            raise ValueError('no function named %s' % func_name)            
        setattr(self, 'find', getattr(self.pattern, func_name))
        
    def set_strfunc (self, func_name):
        if func_name not in self._cmpfuncs:
            raise ValueError('no function named %s' % func_name)            
        setattr(self, 'search', getattr(self, func_name))

    def re (self, to_match):
        return list(filter(self.pattern.match, to_match[self.start:self.end]))

    def sre (self, to_match):
        return self.pattern.match(''.join(to_match[self.start:self.end]))


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
            try:filename = os.path.basename(where)
            except TypeError: filename = '-'
            print("* Searching in %s:" % filename)
        if self.count:
            total = len(list(items))
        for item in items:
            print(item)
        if self.count:
            print("* [%s] Found %d items" % (filename, total))

    def search(self, args):
        for arg in args:
            if arg == sys.stdin:
                archive = zipfile.ZipFile(io.BytesIO(sys.stdin.buffer.read()))
            else:
                archive = zipfile.ZipFile(arg)
            table = Handler()
            parse(archive.open('content.xml'), table)
            self.print_items(list(filter(self.compare, table.rows)), arg)
            archive.close()
                


if __name__ == '__main__':
    parser = check_command_line()
    parsed = parser.parse_args()
    pattern = parsed.pattern if parsed.regex else re.escape(parsed.pattern)
    pattern = re.compile(pattern, parsed.case)
    finder = Finder(pattern, parsed.start, parsed.end)
    finder.set_strfunc(parsed.stringify)
    finder.set_findfunc('match' if parsed.regex else 'search')
    OOoSearch(finder.search, parsed.count, parsed.verbose).search(parsed.files)

