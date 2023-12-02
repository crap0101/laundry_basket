#!/usr/bin/env python3
#
# Lists transmission's torrents.
#
# author: Marco Chieppa | crap0101
#

#XXX+TODO: add info choices

import argparse
import getpass
import os
import re
if not hasattr(re, "NOFLAG"):
    setattr(re, "NOFLAG", 0) # added in python 3.11
import sys

import transmissionrpc

_HOST = 'localhost'
_PORT = 9091
_OUTFILE = sys.stdout

def get_args (args=None):
    p = argparse.ArgumentParser(
        description="*** Lists transmission's torrents ***")
    p.add_argument('-H', '--host',
                   dest='host', default=_HOST,
                   help='Transmission RPC host (default: %(default)s)')
    p.add_argument('-P', '--port',
                   dest='port', type=int, default=_PORT,
                   help='Transmission RPC port (default: %(default)s)')
    p.add_argument('-u', '-user',
                   dest='user', default=None, help='user name')
    p.add_argument('-o', '--outfile',
                   dest='outfile', default=_OUTFILE, metavar='PATH',
                   help="outputs to %(metavar)s (default: %(default)s)")
    p.add_argument('-r', '--regex',
                   dest='regex', metavar='STRING',
                   help="a regex matching torrent's name")
    p.add_argument('-i', '--ignore-case',
                   dest='regex_flag', action='store_true',
                   help="for case-insensitive regex match.")
    pg = p.add_mutually_exclusive_group()
    pg.add_argument('-p', '--psw',
                    dest='psw', default=None,
                    help=('password. If a connection can be established'
                          ' without a password, use -n/--no-psw, otherwise'
                          ' you will be asked for (if not provided)'))
    pg.add_argument('-n', '--no-psw',
                    dest='no_psw', action='store_true',
                    help=('Use this option if yuo can connect without'
                          ' a password, otherwise you will be asked for'
                          ' (if not provided by the -p/--psw option)'))
    return p, p.parse_args()


def main (host, port, user, psw, out, regex, re_flag):
        client = transmissionrpc.Client(address=host, port=port,
                                user=user, password=psw)
        torrents = client.get_torrents()
        if regex:
            for t in torrents:
                if re.search(regex, t.name, re_flag):
                    print(os.path.join(t.downloadDir, t.name), file=out)
        else:
            for t in torrents:
                print(os.path.join(t.downloadDir, t.name), file=out)


if __name__ == '__main__':
    parser, args = get_args()
    if not args.no_psw and not args.psw:
        if args.user is None:
            parser.error("authentication with password requires a username.")
        args.psw = getpass.getpass('password: ')

    if args.regex_flag:
        args.regex_flag = re.I
    else:
        args.regex_flag = re.NOFLAG
    with (open(args.outfile, 'w')
          if (args.outfile != _OUTFILE)
          else args.outfile) as outfile:
        main(args.host, args.port, args.user, args.psw,
             outfile, args.regex, args.regex_flag)

