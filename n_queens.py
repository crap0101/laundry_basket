#!/usr/bin/env python

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


from __future__ import print_function
import argparse
import itertools as it
import sys
if sys.version_info.major < 3:
    input = raw_input

_VERSION = '0.5'
DESCRIPTION = 'n-queen puzzle'

def nqueens(n):
    def safe_pos(nrow, queens):
        safe = set()
        for ncol in range(n):
            cell = (nrow, ncol)
            if not queens:
                safe.add(cell)
                continue
            for row, col in queens:
                if (col == ncol
                    or (nrow, col-(nrow-row)) == cell
                    or (nrow, col+(nrow-row)) == cell):
                    break
            else:
                safe.add(cell)
        return safe
    def place(nrow, queens):
        if nrow == n:
            yield queens
        else:
            for pos in safe_pos(nrow, queens):
                q = queens[:]
                q.append(pos)
                for c in place(nrow+1, q):
                    yield c
    for comb in place(0, []):
        yield comb

def print_q(n, combinations, view_max=0, interactive=False):
    _separator = "# "*n
    _continue = input if interactive else print
    r, s = (float('inf'), '') if view_max < 1 else (view_max, 'partial')
    c = -1
    for c, queens in enumerate(combinations):
        for row, q in enumerate(queens):
            print(" ".join(("Q" if (row, col) == q else '-')
                    for col in range(n)))
        if c >= r-1:
            break
        _continue(_separator)
    print(c+1, '%s solutions' % s)
    
if __name__ == '__main__':
    p = argparse.ArgumentParser(description=DESCRIPTION)
    p.add_argument('queens', type=int, help='number of queens')
    p.add_argument('-i', '--interactive',
                   action='store_true', dest='interactive',
                   help='interactive mode')
    p.add_argument('-m', '--view-max',
                   dest='view_max', type=int, default=0, metavar='NUMBER',
                   help='view max NUMBER results.')
    p.add_argument('-v', '--version', action='version', version=_VERSION)
    args = p.parse_args()
    combinations = nqueens(args.queens)
    print_q(args.queens, combinations, args.view_max, args.interactive)
