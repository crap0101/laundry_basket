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
import sys

_EXTS = ('RW2', 'CR2', 'dng')
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
    p.add_argument('-t', '--test',
                   dest='tests', action='store_true', help='run tests')
    return p.parse_args(cmdline)

def get_names (path):
    for fn in os.listdir(path):
        if os.path.isfile(os.path.join(path, fn)):
            yield fn

def remove (basenames, path, exts, ignore=False):
    names = set(os.path.splitext(n)[0] for n in basenames)
    exts = set(".{}".format(e) for e in exts)
    for fn in os.listdir(path):
        n, e = os.path.splitext(fn)
        if e in exts and n not in names:
            try:
                os.remove(os.path.join(path, fn))
                logging.info("removing {}".format(os.path.join(path, fn)))
            except Exception as err:
                if not ignore:
                    raise err
                else:
                    logging.error("ERR ({}): {}".format(fn, err))

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
    if args.orig is None:
        args.orig = os.getcwd()
    if args.add_exts:
        exts = list(_EXTS) + args.add_exts
    elif args.cust_exts:
        exts = args.cust_exts
    else:
        exts = _EXTS
    dest = os.path.join(args.orig, args.dest)
    remove(get_names(args.orig), dest, exts, args.ignore)
