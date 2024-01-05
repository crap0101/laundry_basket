#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2010-2024  Marco Chieppa (aka crap0101)

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


__doc__  = """
Conway's Game of Life with tkinter

COMMANDS:
 * any key: exit the game
 * mouse right button: pause/unpause the universe
 * mouse left button: when the evolution is paused, flip the cells state.
"""

import array
import argparse
import itertools as it
import os
import sys
import random
import time
import tkinter


STICKY = tkinter.N+tkinter.W+tkinter.S+tkinter.E

VERSION = '0.2'

RECT_COLOR = 'red'
BG_COLOR = 'black'
COLOR_LIVE = 'green'
COLOR_DEAD = BG_COLOR
CELL_COLORS = (COLOR_DEAD, COLOR_LIVE)

E_CONFIGURE = 22

def get_parsed (args=None):
    """
    Parse the command line (or the optional *args* sequence
    using argparse and return a Namespace object.
    """
    class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter,
                          argparse.RawDescriptionHelpFormatter):
        pass
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=CustomFormatter)
    parser.add_argument('-c', '--columns',
                         dest='cols', type=int, default=20,
                         metavar='NUM', help="columns")
    parser.add_argument('-r', '--rows',
                         dest='rows', type=int, default=20,
                         metavar='NUM', help="rows")
    parser.add_argument('-d', '--density',
                         dest='density', type=int, default=0,
                         metavar='NUM', help="universe density")
    parser.add_argument('-D', '--delay',
                         dest='delay', type=int, default=300,
                         metavar='NUM', help="ms delay between generations.")
    parser.add_argument('-f', '--zero-fill',
                         action='store_true', dest='zfill',
                         help='''when using -i and no enough data,
                         fill with empty cells.''')
    parser.add_argument('-i', '--initial',
                         dest='optvalues', type=str, default=None,
                         metavar='STRING', help="initial cells values.")
    parser.add_argument('-g', '--print-gen',
                        dest='printg', action='store_true',
                       help="Prints the number of generations reached.")
    parser.add_argument('-H', '--height',
                         dest='h', type=int, default=300,
                         metavar='NUM', help="window height")
    parser.add_argument('-W', '--width',
                         dest='w', type=int, default=300,
                         metavar='NUM', help="window width")
    parser.add_argument('-p', '--print-inittable',
                        dest='printt', action='store_true',
                        help='Prints initial table')
    parser.add_argument('-v', '--version',
                        action='version', version=VERSION)
    return parser.parse_args(args)


###############
### CLASSES ###
###############

class Point (object):
    """(incomplete) Point class."""
    def __init__ (self, x, y):
        self.x = x
        self.y = y
    @property
    def values (self):
        """The Point coordinates."""
        return self.x, self.y
    @values.setter
    def values (self, new_values):
        """Set the Point coordinates (x,y) to *newvalues."""
        self.x, self.y = new_values
    def __eq__ (self, other_point):
        return self.values == other_point
    def __add__ (self, other_point):
        try:
            return Point(self.x + other_point.x, self.y + other_point.y)
        except AttributeError:
            return Point(self.x + other_point[0], self.y + other_point[1])
    __radd__ = __add__
    def __iadd__ (self, other_point):
        self.values = (self + other_point).values
        return self
    def __sub__ (self, other_point):
        try:
            return Point(self.x - other_point.x, self.y - other_point.y)
        except AttributeError:
            return Point(self.x - other_point[0], self.y - other_point[1])
    def __isub__ (self, other_point):
        self.values = (self - other_point).values
        return self
    def __str__ (self):
        return "{}".format(self.values)
    def __repr__ (self):
        return "{}{}".format(self.__class__.__name__, self.values)


class ConwayGame (object):
    """A class which implements the Conway's game of life with tkinter."""
    def __init__ (self, root=None, size=(300,300), gridsize=(20,20),
                  optvalues=None, density=0, delay=100, zfill=True):
        self._root = root
        self._frame = None
        self._canvas = None
        self._loop_id = None
        self._items = {}
        self.delay = delay
        self._playing = True
        self.generations = 0
        self.w, self.h = size
        self.rows, self.cols = gridsize
        self._rect_size = None
        self.old_table = None
        self.table = array.array('I', [0 for x in range(self.cols * self.rows)])
        if not optvalues:
            m = int(min(self.rows, self.cols))
            c = self.cols - 1
            for i in range(self.rows):
                for j in range(int(m ** 0.5 + density)):
                    self.table[i * random.randint(0, c)] = 1
        else:
            if zfill:
                cycle = it.chain(map(int, optvalues), it.cycle([0]))
            else:
                cycle = it.cycle(map(int, optvalues))
            for p in range(self.rows * self.cols):
                self.table[p] = next(cycle)
        self.neighbors = tuple(
            Point(*p) for p in it.product((-1,0,1), (-1,0,1)) if any(p))
        self.inittable = self.table[:]
        
    def check_alive (self, row, col):
        """
        Check if the cell in the grid at (row,col) is alive.
        Returns the number of neighbors.
        """
        return sum(self.table[p.x * self.cols + p.y]
                   for p in filter(self.in_grid,
                                   [Point(p.x + row, p.y + col)
                                    for p in self.neighbors]))

    def create_state (self, rows=None, cols=None):
        rows = rows or self.rows
        cols = cols or self.cols
        c = cols
        _d = min((self.w, self.h))
        _c = max((rows, cols))        
        dw = (_d // _c) or 1 # int(5/100*_d)
        dh = (_d // _c) or 1 # int(5/100*_d)
        for pr in range(rows):
            for pc in range(cols):
                pos = pr * c + pc
                i = self._canvas.create_oval(
                    pr * dw, pc * dh, pr * dw + dw, pc * dh + dh,
                    fill=CELL_COLORS[self.table[pos]])
                self._items[i] = (pr, pc)
        self._rect_size =  pr * dw + dw, pc * dh + dh
        self._create_rect()

    def in_grid (self, point):
        """Returns True if `point' belongs to the grid."""
        return (-1 < point.x < self.rows) and (-1 < point.y < self.cols)

    def is_eou (self):
        """End Of Universe.
        Returns True if the universe donesn't evolve anymore."""
        return self.table == self.old_table

    def run (self):
        """Start the game."""
        self._frame_config()
        self._canvas_config()

        self._button = tkinter.Button(self._frame, text="update canvas", command=self._update_canvas_size)
        self._button.rowconfigure(0, weight=1)
        self._button.columnconfigure(0, weight=1)
        self._button.grid(row=1, sticky=STICKY)

        self._root = self._frame.winfo_toplevel()
        self._root.rowconfigure(0, weight=1)
        self._root.columnconfigure(0, weight=1)

        self.create_state()
        self._loop_id = self._canvas.after(self.delay, self.update)
        self._frame.mainloop()
        return self.generations

    def step (self):
        """Compute and display another generation in the universe."""
        new_table = self.table[:]
        cols = self.cols
        for item, (r,c) in self._items.items():
            pos = r * cols + c
            alive_val = self.check_alive(r,c)
            if self.table[pos]:
                if alive_val not in (2,3):
                    new_table[pos] = 0
            elif alive_val == 3:
                new_table[pos] = 1
        self.table = new_table[:]
        self.generations += 1
        if self.is_eou():
            return False
        self.old_table = self.table[:]
        return True

    def update (self):
        print('UPDATE:',
              self._canvas.winfo_width(), self._canvas.winfo_height(),
              "|", self.w, self.h, "ITEMS:", len(self._items), end=' ** ')
        if not self._playing and self._loop_id is not None:
            self._canvas.after_cancel(self._loop_id)
            self._loop_id = None
        else:
            evolving = self.step()
            print("evolving:", bool(evolving))
            if not evolving:
                self._playing = False
            cols = self.cols
            for item, (r,c) in self._items.items():
                self._canvas.itemconfig(
                    item, fill=CELL_COLORS[self.table[r * cols + c]])
            self._loop_id = self._canvas.after(self.delay, self.update)

    def _frame_config(self):
        self._frame = tkinter.Frame(self._root)
        self._frame.grid(sticky=STICKY)
        self._frame.rowconfigure(0, weight=1)
        self._frame.columnconfigure(0, weight=1)
        
    def _canvas_config(self):
        self._canvas = tkinter.Canvas(
            self._frame, bg=BG_COLOR, height=self.h, width=self.w)
        self._canvas.bind('<Button-1>', self._toggle_state)
        self._canvas.bind('<Button-3>', self._pause_unpause)
        self._canvas.bind_all('<Configure>', self._resize)
        self._canvas.grid(row=0, sticky=STICKY)
        self._canvas.rowconfigure(0, weight=1)
        self._canvas.columnconfigure(0, weight=1)

    def _create_rect(self):
        print("RECT:", self.rows, self.cols, "+++", self.w, self.h)
        w, h = self._rect_size
        self._canvas.create_rectangle(
            0, 0, w, h, width=2, outline=RECT_COLOR)

    def _resize (self, e):
        print("*** CONFIGURE ***", e.type, e.num, e.width, e.height,
              "|",self._canvas.winfo_width(),self._canvas.winfo_height(),
              "|",self._canvas.winfo_reqwidth(),self._canvas.winfo_reqheight())
        self.w, self.h = e.width, e.height
        
    def _update_canvas_size(self):
        if self._playing:
            self._canvas.after_cancel(self._loop_id)
            self._pause_unpause(None)
        self._canvas_config()
        self.create_state()
        self._loop_id = self._canvas.after(self.delay, self.update)
        self.update()
        if not self._playing:
            self._pause_unpause(None)

    def _pause_unpause (self, e):
        self._playing ^= True
        print("PLAYING:", bool(self._playing))
        if self._playing and self._loop_id is None:
            self._loop_id = self._canvas.after(self.delay, self.update)

    def _toggle_state (self, e):
        if self._playing:
            print("WARNING: can't change state while playing...")
            return
        try:
            self._canvas.update_idletasks()
            item = self._canvas.find_closest(e.x, e.y)[0]
            r, c = self._items[item]
            cols = self.cols
            self.table[r * cols + c] ^= 1
            self._canvas.itemconfig(
                item, fill=CELL_COLORS[self.table[r * cols + c]])
        except IndexError:
            print("WARNING: no items at table[{}]".format(r*cols+c))
        except KeyError:
            print("WARNING: no items at ({},{}) (gridsize={}x{})".format(
                e.x, e.y, self.rows, self.cols))
        print("TOGGLE at ({},{}) (gridsize={}x{})".format(
            e.x, e.y, self.rows, self.cols))


if __name__ == '__main__':
    args = get_parsed()
    print ((args.w, args.h),
                   (args.rows, args.cols))
    g = ConwayGame(None, (args.w, args.h),
                   (args.rows, args.cols),
                   args.optvalues, args.density,
                   args.delay, args.zfill)
    g.run()

    if args.printt:
        print (repr(g.inittable))
    if args.printg:
        print (repr(g.generations))


"""
# Example for a Glider Gun shooting gliders:

%prog -i 000000000000000000000000100000000000000000000000000000000000000000000000000000000000000000000010100000000000000000000000000000000000000000000000000000000000110000001100000000000011000000000000000000000000000000000000000000000001000100001100000000000011000000000000000000000000000000000000110000000010000010001100000000000000000000000000000000000000000000000000110000000010001011000010100000000000000000000000000000000000000000000000000000000010000010000000100000000000000000000000000000000000000000000000000000000001000100000000000000000000000000000000000000000000000000000000000000000000110000000000000000000000000000000000000000000000000000000000 -c 72 -r 45 -f

# Another, the smallest
%prog -i 000000000000000000000000100000000000000000000000000000000010100000000000000000000000110000001100000000000011000000000001000100001100000000000011110000000010000010001100000000000000110000000010001011000010100000000000000000000010000010000000100000000000000000000001000100000000000000000000000000000000110000000000000000000000 -c 36 -r 36 -f

"""
