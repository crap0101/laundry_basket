#!/usr/bin/env python3

"""
remove a file from DEST if a file with the same name (but
different extension) in ORIG does not exist.
"""

import argparse
import glob
import logging
import os
import os.path
import re
import sys
import urllib.parse

_EXTS = ('RW2', 'CR2', 'ORF', 'dng')
_SFNAME = 'RAW'
_LL = {'NOLOG':logging.CRITICAL+1, 'INFO':logging.INFO, 'ERROR':logging.ERROR}

def get_args (cmdline=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('orig',
                   nargs='?', metavar='ORIG',
                   help='search files here (default to the current dir)')
    p.add_argument('dest',
                   nargs='?', default=_SFNAME, metavar='DEST',
                   help='''remove files from here. This path is relative
                   to ORIG, you must provide an absolute path to override
                   this behaviour. Default: "%(default)s"''')
    p.add_argument('-i', '--ignore-errors',
                   dest='ignore', action='store_true',
                   help='continue even in case of errors')
    e = p.add_mutually_exclusive_group()
    e.add_argument('-e', '--add-extensions',
                   dest='add_exts', nargs='+', metavar='EXT',
                   help=('add these extensions to the default ones to'
                         'search for (default: {})'.format(_EXTS)))
    e.add_argument('-E', '--custom-extensions',
                   dest='cust_exts', nargs='+', metavar='EXT',
                   help='search for these extensions only')
    p.add_argument('-l', '--log-level',
                   dest='loglevel', choices=_LL.keys(),
                   default='INFO', metavar='LEVEL',
                   help='set verbosity, choices: %(choices)s. Default: INFO')
    p.add_argument('-s', '--simulate',
                   dest='simulate', action='store_true',
                   help="show what's going to happen")
    p.add_argument('-t', '--test',
                   dest='tests', action='store_true', help='run tests')
    p.add_argument('-x', '--inexact-match',
                   dest='find_inexact', nargs='?', default=None,
                   const='[_-].*', metavar='PATTERN',
                   help='''Search for inexact matching, i.e. for a file named
                   123.raw without a corresponding file 123.jpg the former will
                   be not removed if a file (for example) named 123-01.jpg or
                   123_edit1.jpg exists. Anyway the raw file will be deleted if
                   the jpg doesn't exist.
                   The way filenames are matched depends upon the value of
                   %(metavar)s, which will be interpreted as a regex pattern
                   following the filename: for example, using -x '[_+]\d{2}$'
                   will match file whose name is followed by an underscore or
                   a plus sign, followed by two digits as in: 123-02.jpg
                   (extensions are stripped off from the filename and don't
                   count for the matching). Default value for %(metavar)s
                   is "%(const)s".''')
    return p.parse_args(cmdline)

def get_names (path):
    for fn in os.listdir(path):
        if os.path.isfile(os.path.join(path, fn)):
            yield fn

def _remove (path, ignore=False):
    try:
        os.remove(path)
        logging.info("removing {}".format(path))
    except Exception as err:
        if not ignore:
            raise err
        else:
            logging.error("ERR ({}): {}".format(fn, err))

def _find_exact (fname, others):
    return fname not in others
def _find_alike (fname, others, pattern):
    return not any(
        (fname == f or re.match("%s%s" % (fname, pattern), f) for f in others))
_find_orphan = _find_exact

def _simulate (path, ignore=False):
    logging.info("[S] removing {}".format(path))

def remove (basenames, path, exts, ignore=False):
    names = set(os.path.splitext(n)[0] for n in basenames)
    exts = set(".{}".format(e) for e in exts)
    for fn in os.listdir(path):
        n, e = os.path.splitext(fn)
        if e in exts and _find_orphan(n, names):
            _remove(os.path.join(path, fn), ignore)

def tests():
    import inspect
    import itertools as it
    from random import randint as _r
    import tempfile
    import shlex
    import subprocess as sbp
    import unittest
    # const
    PYTHON_EXE = sys.executable
    PROGFILE = __file__
    # help functions
    def populate_with(path, exts):
        enmap = {e:[] for e in exts}
        for e in enmap.keys():
            for i in range(_r(5,20)):
                f = tempfile.NamedTemporaryFile(
                    dir=path, suffix='.{}'.format(e), delete=False)
                enmap[e].append(f.name)
        return enmap
    # test objects
    def _setUp(self):
        self.basepath_t = tempfile.TemporaryDirectory()
        self.basepath = self.basepath_t.name
        self.dest = None
        logging.debug("setup method of", self.__class__.__name__, self.basepath)
    def _tearDown(self):
        self.basepath_t.cleanup()
        if self.dest is not None:
            try:
                self.dest.cleanup()
            except OSError as err:
                # maybe just deleted by self.basepath_t's cleaup, when subfolder
                if err.errno != errno.ENOENT:
                    raise err
        logging.debug("teardown method of", self.__class__.__name__)
    class TestWorking(unittest.TestCase):
        setUp = _setUp
        tearDown = _tearDown
        def testStd(self):
            splitext = os.path.splitext
            enmap = populate_with(self.basepath, ('jpg', 'png'))
            nodest_orig_map = populate_with(self.basepath, ('jpg', 'png'))
            subpath = os.path.join(self.basepath, _SFNAME)
            os.mkdir(subpath)
            del_dest_map = populate_with(subpath, _EXTS)
            for fp in  it.chain(*enmap.values()):
                fn = os.path.basename(fp)
                for e in _EXTS:
                    n = '{}.{}'.format(splitext(fn)[0], e)
                    with open(os.path.join(subpath, n), 'w') as f:
                        pass
            remove(get_names(self.basepath), subpath, _EXTS)
            for p in it.chain(*enmap.values()):
                self.assertTrue(os.path.isfile(p))
                fn = splitext(os.path.basename(p))[0]
                for e in _EXTS:
                    self.assertFalse(os.path.exists(os.path.join(subpath, fn)))
            for p in it.chain(*nodest_orig_map.values()):
                self.assertTrue(os.path.isfile(p))
            for p in it.chain(*del_dest_map.values()):
                self.assertFalse(os.path.isfile(p), p)
    class TestCmdLine (unittest.TestCase):
        pass #maybe
    # run tests
    no_map = [(n,o) for n,o in locals().items()
        if n.startswith('Test') and inspect.isclass(o)]
    suite = unittest.TestSuite()
    for n,o in no_map:
        for name, value in inspect.getmembers(o):
            if name.startswith('test') and inspect.isfunction(value):
                logging.debug('+test:', n, name)
                suite.addTest(o(name))
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__':
    args = get_args()
    if args.tests:
        logging.basicConfig(format='%(message)s', level=_LL['NOLOG'])
        tests()
        sys.exit(0)
    logging.basicConfig(format='%(message)s', level=_LL[args.loglevel])
    if args.simulate:
        _remove = _simulate
    if args.find_inexact is not None:
        _find_orphan = lambda f, lst: _find_alike(f, lst, args.find_inexact)
    if args.orig is None:
        orig = urllib.parse.unquote(os.getcwd())
    else:
        orig = urllib.parse.unquote(args.orig)
    if args.add_exts:
        exts = list(_EXTS) + args.add_exts
    elif args.cust_exts:
        exts = args.cust_exts
    else:
        exts = _EXTS
    dest = os.path.join(orig, urllib.parse.unquote(args.dest))
    remove(get_names(orig), dest, exts, args.ignore)
