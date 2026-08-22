#!/usr/bin/env python
# -*- coding: utf-8 -*-
# an enhanced dirname shell tool

# Copyright (C) 2026 Marco Chieppa aka crap0101

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not see <http://www.gnu.org/licenses/>

import argparse
import functools
import os
# @ https://github.com/crap0101/files_stuff
from files_stuff.paths import expand_path, deep_dirname, split_path

_DESC = """
Returns the dirname component of *path*, or the empty string for
components out of range.
By default acts as the usual *nix's dirname shell command.
If no path separator is found, returns '.' (assuming the current dir).

The -C option permits to get a portion of *path* at the specified sublevel;
note that no check is performed about the consistence of its value and the one
of the -l option, so strange results can happens!
Also note, this option conflicts with the -c option.

Examples:
~$ dirname.py foo/bar/baz/spam 
foo/bar/baz
~$ dirname.py -l 2 foo/bar/baz/spam 
foo/bar
~$ dirname.py -C 2 foo/bar/baz/spam 
bar/baz
~$ dirname.py -l 11 foo/bar/baz/spam 

~$ dirname.py -o '*' -l 11 foo/bar/baz/spam 
*
crap0101@debian:~$ dirname.py foo/../bar
foo/..
crap0101@debian:~$ dirname.py -n foo/../bar # normalized, gets "bar"
.
crap0101@debian:~$ dirname.py bar
.
"""

_PM_DESC = """
By default, input paths are manipulated raw.
These options makes some changes on them.
Operations are performed in the order of the command line options.
Possible but pointess: repeated options."""

def get_parser ():
    parser = argparse.ArgumentParser(
        description=_DESC,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-l', '--level',
                        dest='level', type=int,
                        default=1, metavar='INT',
                        help='''A number, the Nth preceding level of the tree from *path*.
                        default: %(default)s, the canonical's *nix dirname behaviour.
                        NOTE: level=0 produces the empty string
                        while level=N with N<0 gives you the Nth path component from the root.''')
    c = parser.add_mutually_exclusive_group()
    c.add_argument('-c', '--component',
                   dest='single_component', action='store_true',
                   help="Prints only the path's component at the given level.")
    c.add_argument('-C', '--cut-at',
                   dest='cut', type=int, default=0, metavar='INT',
                   help="""Cut the resulting path at the given sublevel (as the -l option).
                   Stress about this: the operation is performed on the path
                   obtained AFTER the execution of the -l option""")
    parser.add_argument('-o', '--oor-value',
                        dest='oor', default='', metavar='STR',
                        help="""Use %(metavar)s instead of the empty string for inconsistent results
                        (typically for wrong level/sublevel selection).""")
    parser.add_argument('-z', '--zero',
                        dest='zero',
                        action='store_true',
                        help="end each output line with NUL, not newline.")
    parser.add_argument('paths',
                        default=[], nargs='+', metavar='PATH',
                        help="Prints dirname of the given %(metavar)s.")
    path_manipulation = parser.add_argument_group(
        'PATH MANIPULATION', _PM_DESC)
    path_manipulation.add_argument(
        '-A', '--all',
        dest='manipulate_all',
        action='store_true',
        help="""Expandes user's home dir, environment variables
        and gives a normalized absolutized version of the path.""")
    path_manipulation.add_argument(
        '-u', '--expand-user',
        dest='manipulate_func',
        action='append_const', const=os.path.expanduser,
        help="""Expandes user's home dir.""")
    path_manipulation.add_argument(
        '-v', '--expand-vars',
        dest='manipulate_func',
        action='append_const', const=os.path.expandvars,
        help="""Expandes environment variables.""")
    path_manipulation.add_argument(
        '-a', '--absolute',
        dest='manipulate_func',
        action='append_const', const=os.path.abspath,
        help="""Makes a normalized absolutized version of the path.""")
    path_manipulation.add_argument(
        '-n', '--nornalize',
        dest='manipulate_func',
        action='append_const', const=os.path.normpath,
        help="""Makes (only) a normalized version of the path.""")
    return parser

if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    linesep = '\0' if args.zero else '\n'
    if args.manipulate_all:
        mnpfunc =  expand_path
    elif not args.manipulate_func:
        mnpfunc = lambda p:p
    else:
        mnpfunc = lambda path: functools.reduce(lambda p, f: f(p), args.manipulate_func, path)
    for path in args.paths:
        path = mnpfunc(path)
        if not os.path.split(path)[0]:
            # no path separator in *path*, assuming current dir
            # NOTE: using the -a option makes this useless
            print(os.path.curdir, end=linesep)
        else:
            dn = deep_dirname(path, -args.level, args.single_component)
            if not dn:
                print(args.oor, end=linesep)
            else:
                if args.cut:
                    try:
                        dn = os.path.join(*list(split_path(dn))[-args.cut:])
                        print(dn, end=linesep)
                    except TypeError: # out of range
                        print(args.oor, end=linesep)
                else:
                    print(dn, end=linesep)

