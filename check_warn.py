#!/usr/bin/env python3
# Copyright (C) 2026  Marco Chieppa (aka crap0101)

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

__doc__ = """
@author: Marco Chieppa | crap0101
@version: 0.1
@date: 2026-09-12

Compiles the *.py files in the given path in ANOTHER directory.
Designed to check for warnings.
"""


import os
import py_compile
import shutil
import tempfile

# @ https://github.com/crap0101/files_stuff
from files_stuff import filelist, paths


def get_temp_dest (delete=True):
    return tempfile.TemporaryDirectory(delete=delete)

def get_filenames (basepath, patterns):
    for f in filelist.find(basepath):
        if paths.check_pattern(f, patterns):
            yield f

def clean (tempdir, is_tempdir):
    if is_tempdir:
        tempdir.cleanup()
    else:
        shutil.rmtree(tempdir)

        
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-d', '--destdir', dest='destdir', default=None, metavar='PATH',
                        help='Puts here *.pyc files. Default: creates a tmp dir. Deletes it when done.')
    parser.add_argument('-n', '--nodelete', dest='nodelete', action='store_true',
                        help='Does not delete the used temp dir.')
    parser.add_argument('-p', '--patterns', dest='patterns', nargs='+',
                        default=['*.py'], metavar='PATTERN',
                        help='Use %(metavar)s to individuate files. Default: %(default)s')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                        help='Be verbose')
    parser.add_argument('basepath', nargs='?', default=os.getcwd(), metavar='PATH',
                        help='Searching dir, default to the current working dir.')
    
    args = parser.parse_args()
    delete_on_exit = not args.nodelete
    is_tempfile_dir = False
    _tmpdestdir = None

    if args.destdir is not None:
        if not args.destdir:
            parser.error(f"invalid destination path: '{destdir}'")
        destdir = args.destdir
    else:
        _tmpdestdir = get_temp_dest(delete_on_exit)
        destdir = _tmpdestdir.name
        is_tempfile_dir = True

    if args.verbose:
        print(f"* search dir: {args.basepath}\n* writing pyc in: {destdir}\n* delete on exit: {delete_on_exit}")

    for f in get_filenames(args.basepath, args.patterns):
        d = os.path.join(destdir, os.path.splitext(os.path.basename(f))[0]) + '.pyc'
        if args.verbose:
            print(f'compiling "{f}" to "{d}"')
        py_compile.compile(f, cfile=d)

    if delete_on_exit:
        clean(_tmpdestdir if is_tempfile_dir else destdir, is_tempfile_dir)
