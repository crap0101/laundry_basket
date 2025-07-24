#!/usr/bin/env python3
#
# written by: Marco Chieppa (aka crap0101, 2016-05-09)
#

import argparse
import getpass
import re

import transmissionrpc

def get_args (args=None):
    p = argparse.ArgumentParser(
        description="*** remove trackers from transmission's torrents ***")
    p.add_argument('-H', '--host',
                   dest='host', default='localhost',
                   help='Transmission RPC host (default: %(default)s)')
    p.add_argument('-P', '--port',
                   dest='port', type=int, default=9091,
                   help='Transmission RPC port (default: %(default)s)')
    p.add_argument('-r', '--regex',
                   dest='regex', metavar='STRING',
                   help="a regex matching tracker's name")
    p.add_argument('-s', '--simulate',
                   dest='simulate', action='store_true',
                   help='show what trackers would have been removed')
    p.add_argument('-u', '-user',
                   dest='user', default=None, help='user name')
    pg = p.add_mutually_exclusive_group()
    pg.add_argument('-p', '--pswd',
                    dest='pswd', default=None,
                    help=('password. If a connection can be established'
                          ' without a password, use -n/--no-pswd, otherwise'
                          ' you will be asked for (if not provided)'))
    pg.add_argument('-n', '--no-pswd',
                    dest='no_pswd', action='store_true',
                    help=('Use this option if yuo can connect without'
                          ' a password, otherwise you will be asked for'
                          ' (if not provided by the -p/--pswd option)'))
    return p, p.parse_args()

def show (torrents, regex):
    reg = re.compile(regex)
    for torrent in torrents:
        trackers_to_remove = set()
        for t in torrent.trackers:
            if reg.match(t['announce']):
                trackers_to_remove.add(t['announce'])
            if reg.match(t['scrape']):
                trackers_to_remove.add(t['scrape'])
        if trackers_to_remove:
            print("remove from <{}> matches: <{}>".format(
                torrent.name, list(trackers_to_remove)))

def remove (torrents, regex):
    reg = re.compile(regex)
    for torrent in torrents:
        trackers_to_remove = []
        for tracker in torrent.trackers:
            if reg.match(tracker['announce']) or reg.match(tracker['scrape']):
                trackers_to_remove.append(tracker['id'])
        if trackers_to_remove:
            client.change_torrent(torrent.id, trackerRemove=trackers_to_remove)

if __name__ == '__main__':
    #XXX+TODO: show some more info
    parser, args = get_args()
    if not args.no_pswd and not args.pswd:
        if args.user is None:
            parser.error("authentication with password requires a username")
        args.pswd = getpass.getpass('password: ')
    if args.simulate:
        doit = show
    else:
        doit = remove
    client = transmissionrpc.Client(
        args.host, port=args.port, user=args.user, password=args.pswd)
    torrents = client.get_torrents()
    doit(torrents, args.regex)

