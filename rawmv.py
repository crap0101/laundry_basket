#!/usr/bin/env python3
#
# author: Marco Chieppa | crap0101
#

"""
given a path, create a sub-folder and move selected files into it
"""

import argparse
import errno
import glob
import os
import os.path
import shutil
import sys
import urllib.parse

_EXTS = ('RW2', 'CR2', 'ORF', 'dng')
_SFNAME = 'RAW'

def _debug(*a, **k):
    print(*a, file=sys.stderr, **k)

def get_args (cmdline=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('orig',
                   nargs='?', metavar='ORIG',
                   help=('base path, search here for files'
                         ' (default to the current dir)'))
    p.add_argument('-d', '--dest', dest='dest', default=_SFNAME,
                   metavar='DEST',
                   help=('move files here. Destination path relative to ORIG,'
                         ' you must provide an absolute path to override this'
                         ' behaviour. Default: "%(default)s"'))
    p.add_argument('-i', '--ignore-exists',
                   dest='replace', action='store_true',
                   help='''continue even if DEST (or any files to be copied in)
                   already exists; existing files will be replaced.''')
    e = p.add_mutually_exclusive_group()
    e.add_argument('-e', '--add-extensions',
                   dest='add_exts', nargs='+', metavar='EXT',
                   help=('add these extensions to the default ones to search'
                         ' for (default: {})'.format(_EXTS)))
    e.add_argument('-E', '--custom-extensions',
                   dest='cust_exts', nargs='+', metavar='EXT',
                   help='search for these extensions only')
    p.add_argument('-t', '--test',
                   dest='tests', action='store_true', help='run tests')
    return p.parse_args(cmdline)

def get_paths (path, exts):
    for e in exts:
        for p in glob.glob(os.path.join(path, '*.{}'.format(e))):
            yield p

def _secure_move(orig, dest, replace=True):
    """ Try to move *orig* to *dest*;
    if fails try to _copy_ *orig* to *dest*, then delete orig.
    If *replace* is a true value (default) overwrite *dest* if already exists,
    raise OSError otherwise.
    """
    if hasattr(os, 'replace'): # replace introduced in python 3.3
        mv = os.replace if replace else os.rename
    else:
        mv = os.rename
    # on some *nix even os.rename can works if *dest* already exists,
    # so uniform this function's behaviour
    if not replace and os.path.exists(dest):
        err = OSError(os.strerror(errno.EEXIST))
        err.errno = errno.EEXIST
        raise err
    try:
        # on some *nix moving files to different file systems may fail
        mv(orig, dest)
    except OSError as err:
        #_debug("raised:",err)
        if err.errno == errno.EXDEV:
            shutil.copy2(orig, dest)
            os.remove(orig)
        else:
            raise err

def move (paths, dest, replace=False):
    for p in paths:
        fn = os.path.split(p)[1]
        try:
            _secure_move(p, os.path.join(dest, fn), replace)
        except OSError as err:
            raise err

def tests ():
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
        #_debug("setup method of", self.__class__.__name__, self.basepath)
    def _tearDown(self):
        self.basepath_t.cleanup()
        if self.dest is not None:
            try:
                self.dest.cleanup()
            except OSError as err:
                # maybe just deleted by self.basepath_t's cleaup, when subfolder
                if err.errno != errno.ENOENT:
                    raise err
        #_debug("teardown method of", self.__class__.__name__)
    class TestWorking(unittest.TestCase):
        setUp = _setUp
        tearDown = _tearDown
        def testStd(self):
            enmap = populate_with(self.basepath, _EXTS)
            fnames = os.listdir(self.basepath)
            subpath = os.path.join(self.basepath, _SFNAME)
            os.mkdir(subpath)
            move(get_paths(self.basepath, _EXTS), subpath)
            for p in it.chain(*enmap.values()):
                self.assertFalse(os.path.isfile(p))
            for name in fnames:
                self.assertTrue(os.path.isfile(os.path.join(subpath, name)))
        def testDifferentPaths(self):
            enmap = populate_with(self.basepath, _EXTS)
            fnames = os.listdir(self.basepath)
            self.dest = tempfile.TemporaryDirectory()
            subpath = self.dest.name
            move(get_paths(self.basepath, _EXTS), subpath)
            for p in it.chain(*enmap.values()):
                self.assertFalse(os.path.isfile(p))
            for name in fnames:
                self.assertTrue(os.path.isfile(os.path.join(subpath, name)))
        def testMiscFiles(self):
            enmap = populate_with(self.basepath, _EXTS)
            othersmap = populate_with(self.basepath, ('txt','jpg','py'))
            fnames = os.listdir(self.basepath)
            self.dest = tempfile.TemporaryDirectory()
            subpath = self.dest.name
            move(get_paths(self.basepath, _EXTS), subpath)
            for p in it.chain(*enmap.values()):
                self.assertFalse(os.path.isfile(p))
                self.assertTrue(
                    os.path.isfile(os.path.join(subpath, os.path.split(p)[1])))
            for p in it.chain(*othersmap.values()):
                self.assertTrue(os.path.isfile(p))
                self.assertFalse(
                    os.path.isfile(os.path.join(subpath, os.path.split(p)[1])))
    class TestCmdln(unittest.TestCase):
        setUp = _setUp
        tearDown = _tearDown
        def testOk(self):
            cmd_dict = {'exe': PYTHON_EXE,
                        'orig': self.basepath,
                        'dest': None,
                        'exts': ' '.join(_EXTS),
                        'prog': PROGFILE}
            commands = [
                "{exe} {prog} {orig} -d {dest}",
                "{exe} {prog} -d {dest} {orig}",
                "{exe} {prog} -d {dest} {orig} -e {exts}",
                "{exe} {prog} -E {exts} -d {dest} {orig}",
                ]
            for cmd in commands:
                self.dest = tempfile.TemporaryDirectory()
                cmd_dict['dest'] = self.dest.name
                self.dest.cleanup()
                populate_with(self.basepath, _EXTS)
                cmdline = shlex.split(cmd.format(**cmd_dict))
                pipe = sbp.Popen(cmdline, stdout=sbp.PIPE, stderr=sbp.PIPE)
                stderr = pipe.communicate()[1].decode('utf-8')
                retcode = pipe.returncode
                self.assertEqual(retcode, 0,
                                 "Retcode == {} | cmd: {} | stderr: {}".format(
                    retcode, ' '.join(cmdline), ''.join(stderr)))
                # ignore exsisting
                populate_with(self.basepath, _EXTS)
                cmdline.append('-i')
                pipe = sbp.Popen(cmdline, stdout=sbp.PIPE, stderr=sbp.PIPE)
                stderr = pipe.communicate()[1].decode('utf-8')
                retcode = pipe.returncode
                self.assertEqual(retcode, 0,
                                 "Retcode == {} | cmd: {} | stderr: {}".format(
                    retcode, ' '.join(cmdline), ''.join(stderr)))
        def testFail(self):
            self.dest = tempfile.TemporaryDirectory()
            cmd_dict = {'exe': PYTHON_EXE,
                        'orig': self.basepath,
                        'dest': self.dest.name,
                        'exts': ' '.join(_EXTS),
                        'prog': PROGFILE}
            commands = [
                "{exe} {prog} {orig} -d {dest}",
                "{exe} {prog} -d {dest} {orig}",
                "{exe} {prog} -d {dest} {orig} -e {exts}",
                "{exe} {prog} -E {exts} -d {dest} {orig}",
                "{exe} {prog} -E {exts} -e foo bar -d {dest} {orig}",
                ]
            for cmd in commands:
                populate_with(self.basepath, _EXTS)
                cmdline = shlex.split(cmd.format(**cmd_dict))
                pipe = sbp.Popen(cmdline, stdout=sbp.PIPE, stderr=sbp.PIPE)
                pipe.communicate()
                retcode = pipe.returncode
                self.assertNotEqual(retcode, 0)
    # run tests
    no_map = [(n,o) for n,o in locals().items()
        if n.startswith('Test') and inspect.isclass(o)]
    suite = unittest.TestSuite()
    for n,o in no_map:
        for name, value in inspect.getmembers(o):
            if name.startswith('test') and inspect.isfunction(value):
                #_debug('+test:', n, name)
                suite.addTest(o(name))
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
    args = get_args()
    if args.tests:
        tests()
        sys.exit(0)
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
    try:
        os.makedirs(dest)
    except OSError as err:
        if err.errno == errno.EEXIST and not args.replace:
            raise err
        elif err.errno != errno.EEXIST:
            raise err
    move(get_paths(orig, exts), dest, args.replace)
