#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Name: ugenpass
# Version: 0.5
# Author: Marco Chieppa ( a.k.a. crap0101 )
# Last Update: 12 May 2011
# Description: password generator
# Requirement: Python >= 2.7 (or any version with the argparse module)

# Copyright (C) 2012  Marco Chieppa (aka crap0101)

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


from __future__ import print_function, division
import argparse
from collections import defaultdict
from operator import itemgetter
import os
import string
import sys

if sys.version_info.major > 2:
    def urandom (n):
        return map(chr, os.urandom(n))
else:
    urandom = os.urandom
    range = xrange

VERSION = '0.6'
DESCRIPTION = "Generate a password for any input (and integer) argument."

SYMBOLS = set(string.printable).difference(string.whitespace)
REPORT_ALL = 'all'
REPORT_ONLY = 'only'
_NO_REPORT = ''

def ugenpass (symbols, n, randfunc=urandom):
    lst = []
    while len(lst) < n:
        lst.extend(symbols.intersection(randfunc(n)))
    while len(lst) != n:
        lst.pop(sum(map(ord, randfunc(n))) % n)
    return ''.join(lst)

def gen (symbols, lengths, times, func=urandom):
    for _ in range(times):
        for n in lengths:
            yield ugenpass(symbols, n, func)

# Report functions & utility stuff

def sub_split (s, min=2):
    """
    Yield subpatterns from string *s* with
    length *min* at least.
    
    list(sub_split('abc',1))
    ['ab', 'abc', 'bc']
    list(sub_split('abc',1))
    ['a', 'ab', 'abc', 'b', 'bc', 'c']
    """
    l = len(s)
    for i in range(l-min+1):
        for j in range(i+min, l+1):
            yield s[i:j]

def print_report (generated, out=sys.stdout):
    """test and report info about the generation"""
    d = defaultdict(int)
    tot_str = len(generated)
    tot_char = sum(map(len, generated))
    for string in generated:
        for char in string:
            d[char] += 1
    unique_char = len(d)
    print("* unique strings: {} of {}".format(len(set(generated)), tot_str), file=out)
    print("* unique chars: {}".format(unique_char), file=out)
    print("* total chars: {}".format(tot_char), file=out)
    for k, v in sorted(d.items(), key=itemgetter(1)):
        print("{}: {:.2f}% ({} times)".format(k, 100*v/tot_char, v), file=out)
    # sub patterns:
    subp = defaultdict(int)
    for g in generated:
        for s in sub_split(g):
            subp[s] += 1
    tot_subp = sum(subp.values())
    found = dict((k,v) for k,v in subp.items() if v > 1)
    if found:
        print("* Repeated patterns found ({} of {} ({:.2}%)):".format(
            len(found), tot_subp, 100*len(found)/tot_subp), file=out)
        for k,v in sorted(found.items(), key=itemgetter(1)):
            print("{}: found {} times".format(k,v), file=out)
        print("* Repeated pattern max len:",
              len(max(found, key=len)), file=out)
        print("* Max pattern repetitions:", max(found.values()), file=out)
    else:
        print("* NO repeated patterns found ({} of {})".format(
            len(found), tot_subp), file=out)

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=DESCRIPTION)
    p.add_argument('lengths', nargs='*', default=[11],
                    type=int, metavar='NUMBER',
                    help='password(s) length, default: 11')
    p.add_argument('-t', '--times', dest='times',
                   type=int, default=1, metavar='NUMBER',
                   help='''repeate the generations %(metavar)s times,
                   so %%prog 9 8 7 -n 3 generate a total of 9 strings.
                   Default: %(default)s, values <= 0 produces no output.''')
    p.add_argument('-R', '--report', dest='report', nargs='?',
                   default=_NO_REPORT, choices=(REPORT_ALL, REPORT_ONLY),
                   help="""Also run test and report info about the generation.
                   Optional parameter {r_all} prints also the string already
                   produced, {r_only} doesn't (the option alone means {r_only})
                   """.format(r_all=REPORT_ALL, r_only=REPORT_ONLY))
    p.add_argument('-o', '--output', dest='out', default='', metavar='FILE',
                   help='output on %(metavar)s (default: stdout)')
    p.add_argument('-v', '--version', action='version', version=VERSION)
    args = p.parse_args()
    if not args.out or args.out == '-':
        out = sys.stdout
    else:
        out = open(args.out, 'w')
    if args.report != _NO_REPORT:
        generated = list(gen(SYMBOLS, args.lengths, args.times, urandom))
        print_report(generated, out=out)
        if args.report == REPORT_ALL:
            for g in generated:
                print(g, file=out)
    else:
        for x in gen(SYMBOLS, args.lengths, args.times, urandom):
            print(x, file=out)
    if out != sys.stdout:
        out.close()
