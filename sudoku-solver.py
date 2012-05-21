#!/usr/bin/env python3

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


_VERSION = '0.3'

import itertools as it
import re
import sys


def make_cells (rows, subrows):
    cs = []
    for i in range(0, rows*rows, rows*subrows):
        for j in range(i, i+rows, subrows):
            c = []
            for k in range(j, j+rows*2+1, rows):
                c.extend(list(range(k, k+subrows)))
            cs.append(c)
    return cs


"""
>>> make_cells(9, 3)
[[0, 1, 2, 9, 10, 11, 18, 19, 20],
  [3, 4, 5, 12, 13, 14, 21, 22, 23],
    [6, 7, 8, 15, 16, 17, 24, 25, 26],
[27, 28, 29, 36, 37, 38, 45, 46, 47],
  [30, 31, 32, 39, 40, 41, 48, 49, 50],
    [33, 34, 35, 42, 43, 44, 51, 52, 53],
[54, 55, 56, 63, 64, 65, 72, 73, 74],
  [57, 58, 59, 66, 67, 68, 75, 76, 77],
    [60, 61, 62, 69, 70, 71, 78, 79, 80]]
"""

def sudoku_solver (initial_table, ROWS=9, SUB_ROWS=3):
    CELLS = ROWS*ROWS
    _cells = make_cells(ROWS,SUB_ROWS)
    RESOLVED = []
    def get_cell (pos):
        for cell in _cells:
            if pos in cell:
                return cell
        raise ValueError("position %d not in cells" % pos)
    def is_valid (table, position, number):
        for p in get_cell(position):
            if table[p] == number:
                return False
        delta = position % ROWS
        for i in it.chain(list(range(position, -1, -ROWS)),
                          list(range(position, CELLS, ROWS)),
                          list(range(position, position-delta-1, -1)),
                          list(range(position, position+ROWS-delta))):
            if table[i] == number:
                return False
        return True
    def solve (table, pos):
        if pos == CELLS or RESOLVED:
            RESOLVED.append(True)
            return table
        elif table[pos]:
            return solve(table[:], pos+1)
        else:
            for n in range(1, ROWS+1):
                if is_valid(table, pos, n):
                    table[pos] = n
                    res = solve(table[:], pos+1)
                    if res:
                        return res
    return solve(initial_table, 0)

def print_board (table, rows=9, subrows=3):
    line_fmt = ("| %s" % ("%d "*subrows))*subrows +'|'
    sep_fmt = ("+-%s" % ("--"*subrows))*subrows + '+'
    print(sep_fmt)
    for r in range(rows):
        print(line_fmt % tuple(table[r*rows:r*rows+rows]))
        if not (r+1)%subrows:
            print(sep_fmt)

if __name__ == '__main__':
    ex_table = list(map(int, '0430802506000000000000010949000040700006'
                             '08000010200003820500000000000005034090710'))
    table = ex_table
    """ex_table = [0, 3, 0, 0, 6, 0, 1, 0, 2, 7, 0, 0, 0, 9, 3, 0,
             0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 8, 0, 0, 0, 2, 3,
             9, 7, 6, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 9, 5,
             7, 8, 1, 0, 0, 0, 2, 0, 0, 0, 0, 4, 0, 0, 0, 0,
             0, 0, 3, 5, 0, 0, 0, 4, 9, 0, 8, 0, 7, 0, 0, 5, 0]
    #"""
    """
    s = sys.stdin.read()
    table = list(map(lambda x: 0 if x == '.' else int(x),
                     re.findall('(\d+|\.)', s, re.DOTALL)))
    print(s)
    if not table:
        table = ex_table
        print("no input (or not a valid one): using default table")
    #"""
    print("Example:")
    print_board(sudoku_solver(table))
