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

# std imports
import argparse
from collections import defaultdict
from contextlib import closing
import itertools as it
import logging
import operator as op
import random
import shelve
import textwrap
import time
# external import, see https://gitorious.org/bumpo
from bumpo.gameUtils import Table
from bumpo.gameUtils import EmptyObject

# some constants
_VERSION = '0.3 (2012-11-16)'
DESCRIPTION = """
A self-learning tic-tac-toe (aka wick wack woe, aka tris, \
aka tria, aka zero per) program.
"""
EPILOG = textwrap.dedent("""
The first time the program must be run with the {-g FILE} option, e.g.
% prog -g FILE
to create the initial data needed to play; FILE is the output file in which \
store these data. After that, games can be played (human vs human, \
machine vs human or even machine vs machine).
The program can be trained (-t option) to enhance its ability.
""")

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
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=DESCRIPTION, epilog=EPILOG)
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
        p1 = HumanPlayer(parsed.symbol)
        p2 = HumanPlayer(APLAYERS[not APLAYERS.index(parsed.symbol)])
        w = game(p1, p2)
        if w is not None:
            print "winner: %s" % w
        else:
            print "even."
    elif parsed.no_human:
        no_human(parsed.data_file)
    else:
        p1 = HumanPlayer(parsed.symbol)
        p2 = AutoPlayer(APLAYERS[not APLAYERS.index(parsed.symbol)])
        p2.remember(parsed.data_file)
        w = game(p1, p2)
        if w == p2:
            print "winner: %s" % p2.symbol
            p2.win = True
        elif w == p1:
            print "winner: %s" % p1.symbol
        else:
            p2.win = None
            print "even."
        p2.end_actions()

