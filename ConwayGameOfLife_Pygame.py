#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of ImparaParole
# Copyright (c) 2010  Marco Chieppa (aka crap0101)

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
Conway's Game of Life with pygame

REQUIREMENTS: package bumpo

COMMANDS:
 * any key: exit the game
 * mouse right button: pause the evolution (in these days many people
   give the impression to have the right button pressed :-))
 * mouse left button: when the evolution is paused, flip the cell state.
"""

import array
import argparse
import itertools as it
import os
import sys
import random
import time

import pygame

_VERSION = '0.3'

COLOR_LIVE = (50,205,50,255)
COLOR_DEAD = (0,0,0,255)
CELL_COLORS = (COLOR_DEAD, COLOR_LIVE)

DEF_SCR_MODE = pygame.FULLSCREEN

### PARSER DEF, HELP STRINGS AND OTHER STUFFS ###

# DISPLAY HELP STRINGS
H_DENSITY = 'Density for the cell in the the universe to fill with.'
H_DELAY = 'The time (in milliseconds) between generations.'
H_COLUMNS = 'Number of columns'
H_ROWS = 'Number of rows'
H_HEIGHT = "Window height. Default to 0 (fullscreen if -W is 0 too)."
H_WIDTH = "Window width. Default to 0 (fullscreen if -H is 0 too)."
H_OPTVAL = """the initial pattern, must be a string of binary digits.
0 means a dead cell, 1 means a live cell. If the pattern is too short to fill
the universe, it will be repeated until every cell got a value.
If the pattern oversize the universe, the excess will be discarded."""
H_SCR_MODE = """The display mode. SCR_MODE must be one of recognized
pygame's constant for the display, eg:
    FULLSCREEN    for a fullscreen display,
    DOUBLEBUF     is recommended for HWSURFACE or OPENGL,
    HWSURFACE     for hardware accelerated (only in FULLSCREEN),
    OPENGL        for an opengl renderable display,
    RESIZABLE     to make the display window resizeable,
    NOFRAME       for a display window with no border or controls.
For example, to get a fullscreen display, you should pass `-s FULLSCREEN`.
You can include many mode names, useful if you want to combine
multiple types of modes, eg: -s RESIZABLE OPENGL .
If no size argument or any other modes are specified, fall in FULLSCREEN mode.
WARNING: some mode could not be available on your machine."""

# MISC HELP STRING
H_PRINTT = "at the end of the game, print the inital table."
H_PRINTG = "at the end of the game, print the number of generations."
H_DESCRIPTION = __doc__

# OTHER CONSTANTS
SCR_MODE_STRINGS = ('FULLSCREEN', 'DOUBLEBUF', 'HWSURFACE',
                    'OPENGL', 'RESIZABLE', 'NOFRAME')


def get_parsed (args=None):
    """
    Parse the command line (or the optional *args* sequence
    using argparse and return a Namespace object.
    """
    parser = argparse.ArgumentParser(
        description=H_DESCRIPTION,
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # display options
    display = parser.add_argument_group('Display Options')
    display.add_argument('-d', '--density',
                         dest='density', type=int, default=0,
                         metavar='NUM', help=H_DENSITY)
    display.add_argument('-D', '--delay',
                         dest='delay', type=int, default=300,
                         metavar='NUM', help=H_DELAY)
    display.add_argument('-r', '--rows',
                         dest='rows', type=int, default=20,
                         metavar='NUM', help=H_ROWS)
    display.add_argument('-c', '--columns',
                         dest='cols', type=int, default=20,
                         metavar='NUM', help=H_COLUMNS)
    display.add_argument('-i', '--initial',
                         dest='optvalues', type=str, default=None,
                         metavar='STRING', help=H_OPTVAL)
    display.add_argument('-f', '--zero-fill',
                         action='store_true', dest='zfill', help='empty fill')
    display.add_argument('-H', '--height',
                         dest='h', type=int, default=0,
                         metavar='NUM', help=H_HEIGHT)
    display.add_argument('-W', '--width',
                         dest='w', type=int, default=0,
                         metavar='NUM', help=H_WIDTH)
    display.add_argument('-s', '--scr-mode',
                         dest='scr_mode', default=(),
                         nargs='+', metavar='SCR_MODE',
                         choices=SCR_MODE_STRINGS, help=H_SCR_MODE)
    # misc options
    parser.add_argument('-b', '--bumpo-packagedir',
                        dest='bumpo', metavar='PATH',
                        help='basepath of the bumpo package (if not installed)')
    parser.add_argument('-v', '--version',
                        action='version', version=_VERSION)
    parser.add_argument('-p', '--print-inittable',
                        dest='printt', action='store_true', help=H_PRINTT)
    parser.add_argument('-g', '--print-gen',
                        dest='printg', action='store_true', help=H_PRINTG)
    return parser.parse_args(args)


def check_mode (modelist):
    """
    Returns the pygame's video mode for the display combining the modes
    in `modelist' or raise an AttributeError if some modes are unknown.
    """
    mode = 0
    try:
        for _mode in modelist:
            mode |= getattr(pygame, _mode)
    except AttributeError:
        raise AttributeError("ERROR: unknown display mode %s\n" % repr(_mode))
    return mode


### CLASSES ###

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
        return "%s" % (self.values,)
    def __repr__ (self):
        return "%s%s" % (self.__class__.__name__, self.values)


class ConwayGame (object):
    """A class which implements the Conway's game of life with pygame."""
    def __init__ (self, screen, nrows, ncols, optvalues, density, delay, zfill):
        self.screen = screen or pygame.display.set_mode((0,0), DEF_SCR_MODE)
        self.pyGrid = Grid(nrows, ncols)
        self.pyGrid.build(GenericGameObject, cell_size=(2,3))
        self.pyGrid.resize(*self.screen.get_size())
        self.delay = (10, delay)
        self.nrows = nrows
        self.ncols = ncols
        self.old_table = None
        self.generations = 0
        self.table = array.array('I', [0 for x in range(ncols * nrows)])
        if not optvalues:
            for i in range(self.nrows):
                for j in range(int(min(nrows,ncols)**0.5+density)):
                    self.table[i*random.randint(0, ncols-1)] = 1
        else:
            if zfill:
                cycle = it.chain(map(int, optvalues), it.cycle([0]))
            else:
                cycle = it.cycle(map(int, optvalues))
            for p in range(self.nrows*self.ncols):
                self.table[p] = next(cycle)
        self.neighbors = tuple(
            Point(*p) for p in it.product((-1,0,1), (-1,0,1)) if any(p))
        self.inittable = self.table[:]

    def in_grid (self, point):
        """Return True if `point' is in grid."""
        return (-1 < point.x < self.nrows) and (-1 < point.y < self.ncols)

    def check_alive (self, row, col):
        """
        Check if the cell in the grid at (row,col) is alive,
        returning its number of neighbors.
        """
        nearp = filter(self.in_grid,
                       [Point(p.x+row, p.y+col) for p in self.neighbors])
        return sum(self.table[p.x*self.ncols+p.y] for p in nearp)

    def display (self):
        """display the actual generation."""
        radius = min(self.pyGrid[0,0].rect.size)/2
        for value, cell in zip(self.table, self.pyGrid):
            pygame.draw.circle(
                self.screen, CELL_COLORS[value], cell.rect.center, radius, 0)
        pygame.display.update()

    def check_evo (self):
        """Return False if the universe don't evolve anymore."""
        return self.table != self.old_table

    def play (self):
        """Compute and display another generation in the universe."""
        new_table = self.table[:]
        for row in range(self.nrows):
            for col in range(self.ncols):
                alive_val = self.check_alive(row, col)
                cpos = row*self.ncols+col
                if self.table[cpos]:
                    if alive_val not in (2, 3):
                        new_table[cpos] = False
                elif alive_val == 3:
                    new_table[cpos] = True
        self.table = new_table[:]
        self.generations += 1
        self.display()
        if not self.check_evo():
            return False
        self.old_table = self.table[:]
        return True

    def start (self):
        """Start the game."""
        self.display()
        self._playing = True
        while True:
            for event in pygame.event.get():
                if event.type in (pygame.QUIT, pygame.KEYDOWN):
                    return self.generations
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_buttons = pygame.mouse.get_pressed()
                    if mouse_buttons[2]:
                        self._playing ^= True
                    elif mouse_buttons[0] and not self._playing:
                        mouse_pos = pygame.mouse.get_pos()
                        for p, cell in enumerate(self.pyGrid):
                            if cell.rect.collidepoint(mouse_pos):
                                self.table[p] ^= True
                        self.display()
            if self._playing:
                if not self.play():
                    return self.generations
            pygame.time.wait(self.delay[self._playing])


if __name__ == '__main__':
    args = get_parsed()
    if args.bumpo:
        sys.path.insert(0, args.bumpo)
    from bumpo.gameObjects import GenericGameObject, Grid
    pygame.init()
    screen = pygame.display.set_mode((args.w, args.h),
                                     check_mode(args.scr_mode))
    g = ConwayGame(screen, args.rows, args.cols,
                   args.optvalues, args.density, args.delay, args.zfill)
    g.start()
    if args.printt:
        print repr(g.inittable)
    if args.printg:
        print repr(g.generations)


"""
# Example for a Glider Gun shooting gliders:

%prog -i 000000000000000000000000100000000000000000000000000000000000000000000000000000000000000000000010100000000000000000000000000000000000000000000000000000000000110000001100000000000011000000000000000000000000000000000000000000000001000100001100000000000011000000000000000000000000000000000000110000000010000010001100000000000000000000000000000000000000000000000000110000000010001011000010100000000000000000000000000000000000000000000000000000000010000010000000100000000000000000000000000000000000000000000000000000000001000100000000000000000000000000000000000000000000000000000000000000000000110000000000000000000000000000000000000000000000000000000000 -c 72 -r 45 -f

# Another, the smallest
%prog -i 000000000000000000000000100000000000000000000000000000000010100000000000000000000000110000001100000000000011000000000001000100001100000000000011110000000010000010001100000000000000110000000010001011000010100000000000000000000010000010000000100000000000000000000001000100000000000000000000000000000000110000000000000000000000 -c 36 -r 36 -f

"""
