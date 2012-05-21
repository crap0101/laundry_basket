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

_VERSION = '0.5'
DESCRIPTION = "Generate a password for any input (and integer) argument."

import argparse
import os
import string
import sys
if sys.version_info.major > 2:
    def urandom (n):
        return map(chr, os.urandom(n))
else:
    urandom = os.urandom

SYMBOLS = set(string.printable).difference(string.whitespace)

def ugenpass (symbols, n, randfunc=urandom):
    lst = []
    while len(lst) < n:
        lst.extend(symbols.intersection(randfunc(n)))
    while len(lst) != n:
        lst.pop(sum(map(ord, randfunc(n))) % n)
    return ''.join(lst)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=DESCRIPTION)
    p.add_argument('lengths', nargs='*', default=[9],
                    type=int, metavar='NUMBER',
                    help='password(s) length, default: 9')
    p.add_argument('-v', '--version', action='version', version=_VERSION)
    args = p.parse_args()
    for n in args.lengths:
        print(ugenpass(SYMBOLS, n))
