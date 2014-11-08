#!/usr/bin/env python

from __future__ import print_function
import argparse
import glob
import json
import os

BROWSERS = ('firefox', 'abrowser')
DEFAULT_BROWSER = 'abrowser'
#TODO: check those paths
SUBPATHS = {'old': '*.default/sessionstore.js',
                 'new': '*.default/sessionstore-backups/recovery.js'}
PATH_FMT = '~/.mozilla/{browser}/{subpath}'

def get_args (args=None):
    p = argparse.ArgumentParser()
    p.add_argument('-b', '--browser',
                   dest='browser', default='abrowser', help='browser name')
    p.add_argument('-s', '--subpath',
                   dest='subpath', choices=(SUBPATHS.keys()),
                   default='new', help='ehm...')
    return p.parse_args(args)

#OLD: SESSION_FILE = '~/.mozilla/firefox/*.default/sessionstore.js'
#SESSION_FILE = '~/.mozilla/abrowser/*.default/sessionstore-backups/recovery.js'

def current_tabs_url (path):
    with open(path) as f:
        data = json.loads(f.read())
        windows = data['windows']
        for win in windows:
            for tab in win['tabs']:
                yield tab['entries'][-1]['url']
#            for entry in tab['entries']:
#                print(entry['url'])

if __name__ == '__main__':
    args = get_args()
    session_file = PATH_FMT.format(
        browser=args.browser, subpath=SUBPATHS[args.subpath])
    try:
        path = glob.glob(os.path.expanduser(session_file))[0]
    except IndexError:
        raise OSError("can't find {}".format(os.path.expanduser(session_file)))
    for url in current_tabs_url(path):
        print(url)
