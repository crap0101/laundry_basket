#!/usr/bin/env python
#coding: utf-8

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


_VERSION = '0.2'
DESCRIPTION = """
A self-learning tic-tac-toe (aka wick wack woe, aka tris,
aka tria, aka zero per) program
"""

import shelve
from contextlib import closing
import itertools as it
import time
import random
import argparse
import operator as op
from collections import defaultdict
import logging

DEBUG_LEVELS = ('DEBUG', 'INFO', 'WARNING')
DEBUG_LEVEL = 'WARNING'

AP1 = 'X'
AP2 = 'O'
APLAYERS = [AP1, AP2]


def gen_data (outfile):
    with closing(shelve.open(outfile, 'n', 2)) as data:
        pass
    for state, symbol in zip(range(1,10), it.cycle(APLAYERS)):
        with closing(shelve.open(outfile, 'c', 2)) as data:
            if data.get(str(state - 1), None) is not None:
                tables = data[str(state - 1)]
            else:
                tables = [(Table(3, 3), 0)]
            logging.debug(
                "generating state %d from %d table" % (state, len(tables)))
            state_tables = []
            for table, _ in tables:
                if check_win(table) or table.isfull:
                    continue                
                for pos in table.free():
                    new_table = table.copy()
                    new_table[pos] = symbol
                    for t in it.chain([new_table],
                                      rotations(new_table),
                                      reflections(new_table)): 
                        if t in state_tables:
                            break
                    else:
                        state_tables.append(new_table)
            data[str(state)] = list(zip(state_tables, it.repeat(0)))



class Table (object):
    def __init__ (self, rows, columns, empty='', seq=()):
        """
        Create a Table of *row* x *columns* size.
        *empty* is the value for the empty cells (default '').
        If *seq* is provided, must be a sequence; the table will be
        populated with it's items (missing positions are filled
        using *empty*).
        """
        super(Table, self).__init__()
        self._row = rows
        self._col = columns
        self._empty = empty
        self._grid = dict(
            it.takewhile(lambda args: args[0] != empty,
                         it.izip_longest(
                            self.iter_pos(), seq, fillvalue=empty)))

    def __contains__ (self, item):
        return item in self._grid.values()

    def __eq__ (self, other):
        for pos, value in self.items():
            if other[pos] != value:
                return False
        return True

    def __ne__ (self, other):
        return not (self == other)

    def __getitem__(self, item):
        return self._grid[item]

    def __setitem__ (self, item, value):
        self._grid[item] = value

    def __iter__(self):
        return iter(self._grid[pos] for pos in self.iter_pos())

    def __len__ (self):
        return len(self._grid)

    def __str__ (self):
        return "Table object (%d, %d) at %s" % (
            self._row, self._col, hex(id(self)))

    @property
    def empty (self):
        return self._empty

    @property
    def isfull (self):
        """Return True if the table has been completely filled."""
        for value in self.values():
            if value == self.empty:
                return False
        return True

    @property
    def columns (self):
        """The table's columns, as a list of lists."""
        cols = []
        for col in range(self._col):
            cols.append(list(self[row, col] for row in range(self._row)))
        return cols

    @property
    def rows (self):
        """The table's rows, as a list of lists."""
        rows = []
        for row in range(self._row):
            rows.append(list(self[row, col] for col in range(self._col)))
        return rows

    def copy (self):
        """Returns a copy of the table."""
        new_table = Table(self._row, self._col, self.empty)
        for pos, value in self.items():
            new_table[pos] = value
        return new_table

    def diagonal (self, row=0, col=0, topright=False):
        """
        Returns a sequence of the table's values for the diagonal
        starting at *row* and *col*.
        *row* and *col* default to zero, i.e. returns the major diagonal.
        If *topright* is True, return the topright-to-bottomleft diagonal.
        Raise KeyError for *row* or *col* values out of index.
        """
        values = []
        endcol = (self._col, -1)[topright]
        stepcol = (1, -1)[topright]
        for pos in zip(range(row, self._row), range(col, endcol, stepcol)):
            values.append(self[pos])
        return values

    def free (self):
        """Yields the table's empty positions."""
        for pos, value in self.items():
            if value == self.empty:
                yield pos

    def get (self, symbol):
        """Yelds the table's positions which holds *symbol*."""
        for pos, item in self.items():
            if item == symbol:
                yield pos

    def items (self):
        """Yields pairs of ((row, col), value) for each cell in the table."""
        for pos in self.iter_pos():
            yield pos, self[pos]

    def iter_pos (self):
        """Yields the coordinates (row, column) of each cell in the table."""
        for row in range(self._row):
            for col in range(self._col):
                yield row, col

    def major_diagonal (self):
        """Returns the values on the table's major (or main) diagonal.""" 
        return self.diagonal()

    def minor_diagonal (self):
        """Returns the values on the table's minor diagonal.""" 
        values = []
        for pos in zip(range(self._row), range(self._col-1, -1, -1)):
            values.append(self[pos])
        return values

    def pprint (self, format=None):
        """Pretty print row-by-row using *format* or the default one."""
        format = format or "%s "*self._col
        for row in self.rows:
            print format % tuple(row)            

    def reflected_h (self):
        """Returns a (horizontal) reflected _copy_ of the table."""
        seq = it.chain(*list(x[::-1] for x in self.rows))
        return Table(self._row, self._col, empty=self.empty, seq=seq)

    def reflected_v (self):
        """Returns a (vertical) reflected _copy_ of the table."""
        seq = it.chain(*self.rows[::-1])
        return Table(self._row, self._col, empty=self.empty, seq=seq)

    def rotated (self):
        """Return a rotated _copy_ of the table."""
        seq = it.chain(*list(x[::-1] for x in zip(*self.rows)))
        return Table(self._col, self._row, empty=self.empty, seq=seq)

    def transposed (self):
        """Returns a transposed _copy_ of the table."""
        new = Table(self._col, self._row)
        for pos, val in zip(new.iter_pos(), it.chain(*self.columns)):
            new[pos] = val
        return new

    def values (self):
        """Yields the value of each cell in the table."""
        for _, value in self.items():
            yield value


def transposed_all (table):
    t = table
    for i in range(3):
        t = t.transposed()
        yield t

def rotations (table):
    t = table
    for _ in range(3):
        t = t.rotated()
        yield t

def reflections (table):
    return [table.reflected_h(), table.reflected_v()]

def check_win (table):
    for tris in it.chain([table.major_diagonal(), table.minor_diagonal()],
                         table.rows, table.columns):
        if table.empty not in tris and len(set(tris)) == 1:
            return tris[0]

def print_table (table):
    print "_ %s" % ' '.join(map(str,range(len(table.columns))))
    for n, row in enumerate(table.rows):
        print "%d %s" % (n, ' '.join("%1s" % str(x) for x in row))
    print


class AutoPlayer (object):
    def __init__ (self, symbol):
        self._symbol = symbol
        self._data = None
        self._choosed = {}
        self._outfile = 'volatile_%f_%d.memory' % (time.time(), id(self))
        self.win = False

    def __eq__ (self, other):
        return self._symbol == other

    def __ne__ (self, other):
        return not (self == other)

    @property
    def symbol (self):
        return self._symbol

    def end_actions (self):
        self.learn()

    def remember (self, file_or_shelf):
        logging.debug("remember...")
        self._outfile = file_or_shelf
        if isinstance(file_or_shelf, shelve.Shelf):
            self._data = file_or_shelf
        else:
            self._data = shelve.open(self._outfile, 'w', 2)
        logging.debug("done.")

    def learn (self):
        logging.debug("learning...")
        changes = 3 if self.win else (0 if self.win is None else -1)
        if not changes:
            return
        for state, pair in self._choosed.items():
            table, value = pair
            logging.debug("updating state %s" % state)
            tables = self._data[state]
            missed = []
            for pos, t_v in enumerate(tables):
                t, old_value = t_v
                if t == table:
                    tables[pos] = (t, old_value + changes)
                    logging.debug("updating table %s (from %d to %d)"
                                  % (t, old_value, old_value + changes))
                    break
            else:
                missed.append((table, changes))
                logging.debug("missing table... updating...")
            tables.extend(missed)
            self._data[state] = tables
        if not isinstance(self._outfile, shelve.Shelf):
            self._data.close()
        logging.debug("done.")

    def move (self, table, state):
        state = str(state)
        choices = defaultdict(list)
        already_checked = []
        for pos in table.free():
            tt = table.copy()
            tt[pos] = self.symbol
            if tt in already_checked:
                continue
            tables = list(it.chain([tt], rotations(tt), reflections(tt)))
            for t, value in sorted(
                self._data[state], key=op.itemgetter(1), reverse=True):
                if t in tables:
                    choices[value].append((tt, pos))
                    break
            already_checked.extend(tables)
        max_val = max(choices)
        tb, pos = random.choice(choices[max_val])
        self._choosed[state] = (tb, max_val)
        return pos

            
class HumanPlayer (AutoPlayer):
    def __init__ (self, symbol):
        super(HumanPlayer, self).__init__(symbol)

    def remember (self, *args):
        print "humans don't remember"
    def learn (self, *args):
        print 'but they can learn something!'
    def move (self, table, state):
        while True:
            try:
                pos = tuple(map(int, raw_input("move: ").split(',')))
                table[pos]
            except (KeyboardInterrupt, ValueError, KeyError) as err:
                print err
                continue
            if table[pos] == table.empty:
                return pos
            else:
                print "invalid choice"


def game (player1, player2, sleep=0):
    table = Table(3, 3)
    print_table(table)
    for state, player in enumerate(it.cycle((player1, player2)), start=1):
        time.sleep(sleep)
        pos = player.move(table, state)
        table[pos] = player.symbol
        print_table(table)
        winner = check_win(table)
        if winner:
            return winner
        elif table.isfull:
            break


def no_human (data_file, sleep=1):
    shelf = shelve.open(data_file, 'w', 2)
    p1 = AutoPlayer(APLAYERS[0])
    p1.remember(shelf)
    p2 = AutoPlayer(APLAYERS[1])
    p2.remember(shelf)
    w = game(p1, p2, sleep)
    if w == p2:
        print "p2 win %s" % p2.symbol 
        p2.win = True
    elif w == p1:
        print "p1 win %s" % p1.symbol
        p1.win = True
    else:
        print "even."
        p1.win = p2.win = None
    p1.end_actions()
    p2.end_actions()
    shelf.close()
    return w

if __name__ == '__main__':
    def get_parsed ():
        parser = argparse.ArgumentParser(description=DESCRIPTION)
        parser.add_argument('-v', '--version',
                            action='version', version=_VERSION)
        parser.add_argument('data_file', metavar='FILE',
                            help='data file to read/write.')
        parser.add_argument('-T', '--training-games',
                            type=int, dest='games', default=50, metavar='NUM',
                            help='''
                            Number of game to play in training mode, default=
                            %(default)s (ignored in non-training mode).''')
        parser.add_argument('-d', '--debug',
                            choices=DEBUG_LEVELS, dest='debug',
                            default=DEBUG_LEVEL,
                            help='debug level (default=%(default)s).')
        parser.add_argument('-s', '--symbol',
                            choices=(AP1, AP2), dest='symbol', default=AP1,
                            help='symbol to use (default=%(default)s).')
        g_group = parser.add_mutually_exclusive_group()
        g_group.add_argument('-g', '--gen-data',
                            action='store_true', dest='gen_data',
                            help='generate initial data and exit.')
        g_group.add_argument('-t', '--training',
                            dest='training_mode', action='store_true',
                            help="try to enhance program's faculty.")
        g_group.add_argument('-u', '--human-mode',
                            dest='only_human', action='store_true',
                            help='game between humans.')
        g_group.add_argument('-n', '--non-human-mode',
                            dest='no_human', action='store_true',
                            help='game between machines.')
        return parser.parse_args()

    parsed = get_parsed()
    logging.basicConfig(format='%(levelname)s: %(message)s',
                        level=getattr(logging, parsed.debug)) 
    if parsed.gen_data:
        gen_data(parsed.data_file)
    elif parsed.training_mode:
        d = defaultdict(int)
        for n in range(parsed.games):
            d[no_human(parsed.data_file, sleep=0)] += 1
        print "results", d
    elif parsed.only_human:
        logging.warning('to be implemented')
    elif parsed.no_human:
        no_human(parsed.data_file)
    else:
        p1 = HumanPlayer(parsed.symbol)
        p2 = AutoPlayer(APLAYERS[not APLAYERS.index(parsed.symbol)])
        p2.remember(parsed.data_file)
        w = game(p1, p2)
        if w == p2:
            print "%s win" % p2.symbol
            p2.win = True
        elif w == p1:
            print "%s win" % p1.symbol
        else:
            p2.win = None
            print "even."
        p2.end_actions()

