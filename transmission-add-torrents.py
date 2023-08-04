#!/usr/bin/env python3

import argparse
import getpass
import os.path
import sys

import transmissionrpc


def get_args (args=None):
    p = argparse.ArgumentParser()
    p.add_argument('torrents',
                   nargs='+', help='torrents to add')
    p.add_argument('-d', '--download-dir',
                   dest='dest', default=None,
                   help='''download directory (if not provided,
                   use the transmission's default path)''')
    p.add_argument('-H', '--host',
                   dest='host', default='localhost',
                   help='Transmission RPC host (default: %(default)s)')
    p.add_argument('-P', '--port',
                   dest='port', type=int, default=9091,
                   help='Transmission RPC port (default: %(default)s)')
    p.add_argument('-u', '--user',
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


def add_torrents (client, torrents, dest=None):
    if dest is None:
        dest = client.session.download_dir
    failed = []
    for t in torrents:
        try:
            client.add_torrent(t, paused=False, download_dir=dest)
        except transmissionrpc.TransmissionError as err:
            failed.append((t, err))
    return failed


if __name__ == '__main__':
    parser, args = get_args()
    if not args.no_pswd and not args.pswd:
        if args.user is None:
            parser.error("authentication with password requires a username")
        args.pswd = getpass.getpass('password: ')
    client = transmissionrpc.Client(args.host, port=args.port,
                                    user=args.user, password=args.pswd)
    fail = add_torrents(client, args.torrents, args.dest)
    if fail: #TODO: add log(s)
        prog = os.path.basename(sys.argv[0])
        for msg in fail:
            print("{}: {} <{}>".format(prog, *msg))
