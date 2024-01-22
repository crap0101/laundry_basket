#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Name: ugenpass
# Version: 1.1
# Author: Marco Chieppa ( a.k.a. crap0101 )
# Last Update: 2024-01-18
# Description: password generator
# Requirement: Python >= 2.7

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
import random
import string
import sys
import time

if sys.version_info.major > 2:
    def urandom (n, chr_range=256):
        a, b = pair_from_time()
        return (chr((x ^ a ^ b) % chr_range) for x in os.urandom(n))
else:
    def urandom (n, chr_range=256):
        a, b = pair_from_time()
        return (chr((ord(x) ^ a ^ b) % chr_range) for x in os.urandom(n))
    range = xrange

VERSION = '1.1'
DESCRIPTION = "Passwords generator."

SYMBOLS = tuple(set(string.printable).difference(string.whitespace))
STR_CONSTRAINT = {
    2: set(string.digits),
    4: set(string.ascii_uppercase),
    8: set(string.ascii_lowercase),
    16: set(string.punctuation),
}
# Replicate for easy use as constants:
DIG   = 2
UPPER = 4
LOWER = 8
PUNCT = 16
DICT_CONSTRAINT = dict(DIG = DIG, UPPER = UPPER, LOWER = LOWER, PUNCT = PUNCT)

SEP = ''
MAXSIZE = sys.maxsize
REPORT_ALL = 'all'
REPORT_ONLY = 'only'
NO_REPORT = ''
PSW_CHR_LENGTH = 25
PSW_WRD_LENGTH = 8

########################
# GENERATION FUNCTIONS #
########################

def ugenpass (symbols, n, randfunc=urandom):
    lst = []
    symidx = tuple(range(len(symbols)))
    slen = len(symidx)
    _n = n**2
    while len(lst) < _n:
        lst.append(symidx[sum(map(ord, randfunc(n))) % slen])
    while len(lst) != n:
        lst.pop(sum(map(ord, randfunc(n))) % n)
    return tuple(symbols[idx] for idx in lst)


def gen (symbols, lengths, times,
         func=urandom, unique=False, sep='', constraint=0):
    if unique:
        def genfunc(sym, n, func):
            s = set()
            while len(s) < n:
                s |= set(ugenpass(sym, n, func))
            return tuple(s)[:n]
    else:
        genfunc = ugenpass
    for _ in range(times):
        for n in lengths:
            x = genfunc(symbols, n, func)
            if constraint:
                while True:
                    ok, mask = check_constraint(x, constraint)
                    if not ok:
                        x = list(x[1:]) + list(random.choice(list(mask)))
                    else:
                        break
            yield sep.join(x)


def get_words (filepath, wrlen, maxwords):
    with (open(filepath) if filepath != '-' else sys.stdin) as wordsfile:
        s, e = wrlen
        tot = 0
        wlist = []
        for line in wordsfile:
            nw = list(w for w in line.split() if s <= len(w) <= e)
            if tot + len(nw) >= maxwords:
                wlist.extend(nw[:maxwords-tot])
                break
            wlist.extend(nw)  
            tot += len(nw)          
        return wlist


def check_constraint (s, constraint):
    """Checks if the generated sequence $s satisfy
    the $constraint mask, a bitwise OR of the
    constants DIG, UPPER, LOWER and PUNCT.
    Return a tuple of (False, STR_CONSTRAINT[key]) which fails
    or (True, 0) if success.
    """
    for k,v in STR_CONSTRAINT.items():
        masked = constraint & k
        if masked:
            if not (set(s) & STR_CONSTRAINT[masked]):
                return False, STR_CONSTRAINT[masked]
    return True, 0



####################################
# REPORT FUNCTIONS & UTILITY STUFF #
####################################

def pair_from_time ():
    t = time.time()
    a = int(t)
    b = int((t - a) * 1000)
    if b == 0:
        b = random.randrange(10000) ^ int(time.time())
    return a, b


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


def print_report (generated, symbols, out=sys.stdout):
    """test and report info about the generation"""
    d = defaultdict(int)
    tot_str = len(generated)
    tot_char = sum(map(len, generated))
    for string in generated:
        for char in string:
            d[char] += 1
    unique_char = len(d)
    print("* Used: {} of {} symbols ({:.2f}%)".format(
        unique_char, len(symbols), 100*unique_char/len(symbols)), file=out)
    print("* unique strings: {} of {}".format
          (len(set(generated)), tot_str), file=out)
    print("* unique chars: {}".format(unique_char), file=out)
    print("* total chars: {}".format(tot_char), file=out)
    for k, v in sorted(d.items(), key=itemgetter(1)):
        print("{}: {:.2f}% ({} times)".format(k, 100*v/tot_char, v), file=out)
    # repeated chars:
    s_rep_chars = []
    for g in generated:
        gs = set(g)
        if len(gs) != len(g):
            s_rep_chars.append((g, gs))
    if s_rep_chars:
        lrp = len(s_rep_chars)
        print("* strings with repeated chars: {} of {} ({:.2f}%)".format(
            lrp, tot_str, 100*lrp/tot_str), file=out)
        for g, gs in s_rep_chars:
            print("{} ({})".format(
                g, ''.join(x for x in gs if g.count(x) > 1)), file=out)
    else:
        print("* NO strings with repeated chars found", file=out)
    # sub patterns:
    subp = defaultdict(int)
    for g in generated:
        for s in sub_split(g):
            subp[s] += 1
    tot_subp = sum(subp.values())
    found = dict((k,v) for k,v in subp.items() if v > 1)
    if found:
        print("* Repeated patterns found ({} of {} ({:.2f}%):".format(
            len(found), tot_subp, 100*len(found)/tot_subp), file=out)
        for k,v in sorted(found.items(), key=itemgetter(1)):
            print("{}: found {} times".format(k,v), file=out)
        print("* Repeated pattern max len:",
              len(max(found, key=len)), file=out)
        print("* Max pattern repetitions:", max(found.values()), file=out)
    else:
        print("* NO repeated patterns found ({} of {})".format(
            len(found), tot_subp), file=out)


#####################
# PARSING UTILITIES #
#####################

class RangeAction (argparse.Action):
    def __init__ (self,  minvalue=None, maxvalue=None,
                  option_strings='', dest='', nargs=None, **kwargs):
        self._min = minvalue
        self._max = maxvalue
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super(RangeAction, self).__init__(option_strings, dest, **kwargs)
    def __call__ (self, parser, namespace, value, option_string=None):
        if value.count(':') > 1:
            parser.error('{}: wrong format: <{}>'.format(option_string, value))
        iv = []
        for x in value.split(':'):
            if x:
                try:
                    iv.append(int(x))
                except ValueError:
                    parser.error('{}: wrong value: {}'.format(
                        option_string, value))
        if len (iv) == 1:
            if value.startswith(':'):
                start = self._min
                end = iv[0]
            else:
                start = iv[0]
                end = self._max
        elif len (iv) == 2:
            start, end = iv
        else:
            parser.error('{}: wrong format: <{}>'.format(option_string, value))
        if start > end:
            parser.error('{}: wrong format: <{}>'.format(option_string, value))
        if start < self._min:
            parser.error('{}: START value must be >= {}'.format(
                option_string, self._min))
        if end > self._max:
            parser.error('{}: END value must be <= {}'.format(
                option_string, self._max))
        setattr(namespace, self.dest, (start, end))


class IntBoundAction (argparse.Action):
    """
    To accepts values in a specific range only. 
    """
    def __init__ (self, minvalue=None, maxvalue=None,
                  option_strings='', dest='', nargs=None, **kwargs):
        self._min = minvalue or 1
        self._max = maxvalue or MAXSIZE
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super(IntBoundAction, self).__init__(option_strings, dest, **kwargs)
    def __call__ (self, parser, namespace, value, option_string=None):
        val = int(value)
        if val > self._max or val < self._min:
            raise parser.error("{} must be in range {}..{}".format(
                option_string, self._min, self._max))
        setattr(namespace, self.dest, value)


def range_int_bound_factory (cls, minv, maxv):
    def foo(*a, **k):
        return cls(minv, maxv, *a, **k)
    return foo


def get_parser():
    _words_from_file = '-w', '--words-from-file'
    p = argparse.ArgumentParser(description=DESCRIPTION)
    p.add_argument('lengths', nargs='*', default=[],
                    type=int, metavar='LENGTH',
                    help=f'''password(s) length. If not provided, sets to
                    {PSW_CHR_LENGTH} when using the default string generation
                    and to {PSW_WRD_LENGTH} when using the -w option.''')
    p.add_argument('-c', '--constraint',
                   dest='constraint', action='append',
                   choices=DICT_CONSTRAINT.keys(), nargs='+',
                   help='''Adds some constraint to the generated string,
                   forcing to include chars from the DIG (digits), UPPER
                   (uppercase ascii), LOWER (lowercase ascii) or PUNCT
                   (punctuation) sets, or any combinations of them.
                   NOTE: ignored when used in conjunction with the -C option
                   or with the -w option.''')
    p.add_argument('-C', '--all-constraint',
                   dest='all_constraints', action='store_const',
                   const=[DICT_CONSTRAINT.keys()],
                   help='''Use all the constraints available for the -c option.
                   NOTE: ignored when used together the -w option.''')
    p.add_argument('-d', '--distinct', dest='uniq', action='store_true',
                   help='Generates password without repeated characters')
    p.add_argument('-t', '--times', dest='times',
                   type=int, default=1, metavar='NUMBER',
                   help='''Repeates the generation %(metavar)s times,
                   so %%prog 9 8 7 -t 3 generate a total of 9 strings.
                   Default: %(default)s, values <= 0 produces no output.''')
    p.add_argument(*_words_from_file, #'-w', '--words-from-file',
                   dest='words', metavar='FILE',
                   help='''Generates password using words from %(metavar)s.
                   If %(metavar)s is "-" read words from stdin.
                   NOTE: The use of this option disable the -C and -c options.
                   ''')
    p.add_argument('-v', '--version', action='version', version=VERSION)
    wp = p.add_argument_group('password from words specific options')
    wp.add_argument('-l', '--word-length',
                    dest='word_rlen',
                    default=(1,MAXSIZE),  metavar='START[:END]',
                    action=range_int_bound_factory(RangeAction, 1, MAXSIZE),
                   help='''Uses words with length in the %(metavar)s range
                        (default: from 1 up to {}).'''.format(MAXSIZE))
    wp.add_argument('-m', '--max-words',
                    dest='max_words', type=int,
                    default=MAXSIZE, metavar='NUMBER',
                    action=range_int_bound_factory(IntBoundAction, 1, MAXSIZE),
                    help='''Reads at most %(metavar)s words from the input
                        file. Default: %(default)s'''.format(MAXSIZE))
    wp.add_argument('-s', '--word-sep',
                   dest='word_sep', default=' ', metavar='STRING',
                   help='''Uses %(metavar)s as separator when generating
                        password using the {} option (default: "%(default)s").
                        '''.format('/'.join(_words_from_file)))
    report = p.add_argument_group('I/O and report options')
    report.add_argument('-o', '--output',
                        dest='out', default='', metavar='FILE',
                        help='Outputs on %(metavar)s (default: stdout)')
    report.add_argument('-R', '--report',
                        dest='report', nargs='?',
                        default=NO_REPORT, choices=(REPORT_ALL, REPORT_ONLY),
                        help=f"""Also runs test and report info about
                        the generation. Optional parameter '{REPORT_ALL}'
                        prints also the string already produced (the option
                        alone means '{REPORT_ONLY}')""")
    return p

if __name__ == '__main__':
    p = get_parser()
    args = p.parse_args()
    if not args.lengths:
        if args.words:
            args.lengths = [PSW_WRD_LENGTH]
        else:
            args.lengths = [PSW_CHR_LENGTH]
    constr = 0
    __constr = set()
    __minlen = min(args.lengths)
    if __minlen < 1:
        p.error('Invalid lengths: {}'.format(__minlen))
    for lst in (args.all_constraints or args.constraint or []):
        __constr.update(lst)
    if __constr:
        if len(__constr) > __minlen:
            p.error(f'Insufficient length to satisfy constraints: {__minlen}')
        for c in __constr:
            constr |= DICT_CONSTRAINT[c]
    if args.words:
        constr = 0
        try:
            SYMBOLS = tuple(set(
                get_words(args.words, args.word_rlen, args.max_words)))
            if not SYMBOLS:
                p.error("Not enough symbols")
        except Exception as e:
            p.error(e)
        SEP = args.word_sep
    if args.uniq and max(args.lengths) > len(SYMBOLS):
        p.error("Some required length exceed the number of available symbols")
    if not args.out or args.out == '-':
        out = sys.stdout
    else:
        out = open(args.out, 'w')
    if args.report != NO_REPORT:
        generated = list(
            gen(SYMBOLS, args.lengths, args.times,
                urandom, args.uniq, SEP, constr))
        print_report(generated, SYMBOLS, out=out)
        if args.report == REPORT_ALL:
            for g in generated:
                print(g, file=out)
    else:
        for x in gen(SYMBOLS, args.lengths, args.times,
                     urandom, args.uniq, SEP, constr):
            print(x, file=out)
    if out != sys.stdout:
        out.close()
