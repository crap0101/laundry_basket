#!/usr/bin/env python
#
# author: Marco Chieppa | crap0101
#

import argparse
import glob
import json
import os
#
import lz4.block

DEFAULT_BROWSER = 'firefox' # eg: 'firefox', 'iceweasel', 'abrowser'
BROWSER_FLAVOUR_SUBPATH = '*.default-esr' # eg: '*.default', '*.default-release', '*.default-esr'
RECOVERY_SUBPATH = 'sessionstore-backups/recovery.jsonlz4'
TARGET_PATH = '~/.mozilla/{browser}/{flavour}/{recovery_subpath}'
DESCRIPTION = '''List open urls in current browser session.'''

def get_args (args=None):
    p = argparse.ArgumentParser(description=DESCRIPTION)
    p.add_argument('-b', '--browser',
                   dest='browser', default=DEFAULT_BROWSER,
                   help='browser name (%(default)s).')
    p.add_argument('-B', '--browser-flavour',
                   dest='flavour', default=BROWSER_FLAVOUR_SUBPATH,
                   help="browser's flavour path location: (%(default)s).")
    p.add_argument('-d', '--no-decompress',
                   dest='no_decompress', action='store_true',
                   help="for old recovery files which was plain text.")
    p.add_argument('-f', '--file',
                   dest='recovery_file_fullpath',
                   help="""browser's session recovery file, fullpath.
                   With this options -b, -B and -s options will be ignored.""")
    p.add_argument('-s', '--subpath',
                   dest='recovery_subpath', default=RECOVERY_SUBPATH,
                   help="browser's session file subpath location: (%(default)s).")
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
            try:
                yield tab['entries'][-1]['url']
            except IndexError:
                # No entries, maybe moz-extension or other stuff
                pass

if __name__ == '__main__':
    args = get_args()
    if args.recovery_file_fullpath:
        session_file = args.recovery_file_fullpath
    else:
        session_file = TARGET_PATH.format(
            browser=args.browser,
            flavour=args.flavour,
            recovery_subpath=args.recovery_subpath)
    try:
        path = glob.glob(os.path.expanduser(session_file))[0]
    except (IndexError, OSError):
        raise OSError("can't find {}".format(session_file)) from None
    for url in current_tabs_url(path, not args.no_decompress):
        print(url)
