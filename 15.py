#!/usr/bin/env python
#coding: utf-8

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

DESCRIPTION = 'The 15-puzzle (aka Gem Puzzle, Game of Fifteen) game using Tk'
EPILOG = 'mouse buttom-left: MOVE; mouse button right: NEW GAME'

_VERSION = '0.6'

try:
    import tkinter
except ImportError:
    import Tkinter as tkinter
import tkMessageBox
import argparse
import random
import logging


class XV(tkinter.Tk):
    def __init__ (self, w=200, h=200, n=15):
        tkinter.Tk.__init__(self)
        self._frame = self._ngbutton = None
        self.w = w
        self.h = h
        self.n = n + 1
        self._bd = int(1 * self.w / 100)
        self._rc = int(self.n**.5)
        self._cmb = [(-1, 0), (1, 0), (0, 1), (0, -1)]
        self._sticky = ''.join(getattr(tkinter, attr) for attr in 'WENS')
        self._numwidth = len(str(self.n))

    def _check(self, event):
        clicked = event.widget
        gd = clicked.grid_info()
        row, col = list(int(x) for x in (gd['row'], gd['column']))
        logging.info('clicked: %s' % clicked.cget('text'))
        for r, c in self._cmb:
            nrow, ncol = row+r, col+c
            if (nrow not in range(self._rc) or ncol not in range(self._rc)):
                continue
            other = self._frame.grid_slaves(nrow, ncol)[0]
            otext = other.cget('text')
            if not otext:
                clicked.grid(column=ncol, row=nrow, sticky=self._sticky)
                other.grid(column=col, row=row, sticky=self._sticky)
                if self._resolved():
                    self._completed_message()
                break

    def _completed_message(self):
        logging.info("! resolved !")
        tkMessageBox.showinfo(
            '', 'resolved!', default=tkMessageBox.OK)

    def _resolved(self):
        for row in range(self._rc):
            for col in range(self._rc):
                num = (col + self._rc * row) + 1
                text = self._frame.grid_slaves(row, col)[0].cget('text')
                if num == self.n:
                    return True
                if not text or num != int(text):
                    return False
        logging.error("In method *_resolved*: return value is None")

    def main(self):
        self.title('15')
        self.minsize(self.w, self.h)
        self.resizable(True, True)
        self._ngbutton = tkinter.Button(self, text='New Game',
                                        bd=self._bd)
        self._ngbutton.bind('<Button-1>', self._new_game)
        self._ngbutton.grid(column=0, row=0, sticky=self._sticky)
        self._frame = tkinter.Frame(self)
        self._frame.grid(column=0, row=1, sticky=self._sticky)
        self._new_game()
    
    def _new_game(self, *args):
        logging.info("# New Game #")
        _nums = [str(i) for i in range(1, self.n)] + ['']
        random.shuffle(_nums)
        for row in range(self._rc):
            for col in range(self._rc):
                b = tkinter.Button(self._frame, text=_nums.pop(),
                                   anchor=tkinter.CENTER, bd=self._bd,
                                   width=self._numwidth)
                b.bind('<Button-1>', self._check)
                b.bind('<Button-3>', self._new_game)
                b.grid(column=col, row=row, sticky=self._sticky)
        _weight = self.w / self._rc
        for i in range(self._rc):
            self._frame.grid_columnconfigure(i, weight=_weight)
            self._frame.grid_rowconfigure(i, weight=_weight)
        self.grid_columnconfigure(0, weight=_weight/2)
        self.grid_rowconfigure(1, weight=_weight/2)
        self.mainloop()



if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=DESCRIPTION, epilog = EPILOG)
    parser.add_argument('-W', '--width', type=int, default=200,
                        dest='width', metavar='NUM', help='window width.')
    parser.add_argument('-H', '--height', type=int, default=200,
                        dest='height', metavar='NUM', help='window height.')
    parser.add_argument('-n', '--number', type=int, default=15,
                        dest='number', metavar='NUM', help='numbers square.')
    parser.add_argument('-l', '--log', dest='loglevel', default=None,
                        choices=('DEBUG', 'INFO', 'WARNING', 'ERROR'),
                        metavar='STR', help='log level. (Choices: %(choices)s)')
    parser.add_argument('-v', '--version', action='version', version=_VERSION)
    args = parser.parse_args()
    if args.loglevel:
        logging.basicConfig(format='%(filename)s:%(levelname)s:%(message)s',
                            level=getattr(logging, args.loglevel))
    if args.width <= 0 or args.height <= 0:
        parser.error('window dimension must be a positive number.')
    if args.number != 15:
        logging.info('LOL, best wishes!')
    XV(args.width, args.height, args.number).main()
