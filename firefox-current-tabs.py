#!/usr/bin/env python3
#
# author: Marco Chieppa | crap0101
#

import argparse
import glob
import json
import os
#
import lz4.block

BROWSERS = ('firefox', 'iceweasel', 'abrowser')
DEFAULT_BROWSER = 'firefox'
#TODO: check those paths
SUBPATH = '*.default/sessionstore-backups/recovery.jsonlz4'
BASEPATH = {'clean': '~/.mozilla/{browser}/{subpath}',
            'snap':'~/snap/firefox/common/.mozilla/{browser}/{subpath}'}
DESCRIPTION='''List open urls in current(s) browser session.'''

def get_args (args=None):
    p = argparse.ArgumentParser(description=DESCRIPTION)
    p.add_argument('-b', '--browser',
                   dest='browser', default=DEFAULT_BROWSER,
                   choices=BROWSERS, help='browser name.')
    p.add_argument('-d', '--no-decompress',
                   dest='no_decompress', action='store_true',
                   help="if config file is an (old) plain text file.")
    p.add_argument('-p', '--basepath',
                   dest='basepath', choices=(BASEPATH.keys()),
                   default='snap', help="browser's session basepath location.")
    p.add_argument('-s', '--subpath',
                   dest='subpath', default=SUBPATH,
                   help="browser's session file path location: (%(default)s).")
    return p.parse_args(args)

def current_tabs_url (path, decompress):
    if decompress:
        with open(path, 'rb') as f:
            f.read(8) # skip magic
            data = json.loads(lz4.block.decompress(f.read()))
    else:
        with open(path) as f:
            data = json.loads(f.read())
    windows = data['windows']
    for win in windows:
        for tab in win['tabs']:
            yield tab['entries'][-1]['url']


if __name__ == '__main__':
    args = get_args()
    path_fmt = BASEPATH[args.basepath]
    session_file = path_fmt.format(
        browser=args.browser, subpath=args.subpath)
    try:
        path = glob.glob(os.path.expanduser(session_file))[0]
    except IndexError:
        raise OSError("can't find {}".format(os.path.expanduser(session_file)))
    for url in current_tabs_url(path, not args.no_decompress):
        print(url)
