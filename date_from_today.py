#!/usr/bin/env python
#
# author: Marco Chieppa | crap0101
#

import argparse
import datetime
import locale
import sys

_DESCRIPTION = 'date of the nth day from today'
_PROGNAME = 'date_from'

locale.setlocale(locale.LC_ALL, '')

def _parse (args):
    parser = argparse.ArgumentParser(prog=_PROGNAME,
                                     description=_DESCRIPTION)
    parser.add_argument('days_from_today', nargs='*', type=int,
                        help='days from today')
    parser.add_argument('-d', '--delta', type=int, default=0, dest='delta',
                        help="day's padding (could be negative)")
    return parser.parse_args(args)

def from_today(days):
    return datetime.date.today() + datetime.timedelta(days=days)

if __name__ == '__main__':
    ns = _parse(sys.argv[1:])
    for day_from in ns.days_from_today:
        print(datetime.date.strftime(
            from_today(day_from + ns.delta), "%d %B %Y"))
