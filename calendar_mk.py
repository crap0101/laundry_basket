#!/usr/bin/env python3
# python 3.8.10
#
# author: Marco Chieppa | crap0101
#

import argparse
import calendar
import datetime
import itertools
import locale
import sys

locale.setlocale(locale.LC_ALL, '')

def make_cal (year, month, day=1):
    if month == 12:
        next_year = year + 1
        next_month = 1
    else:
        next_year = year
        next_month = month + 1
    start = datetime.date(year, month, day)
    end = datetime.date(next_year, next_month, day)
    dates = []
    for d in calendar.Calendar().itermonthdates(year, month):
        if d >= start and d < end:
            dates.append(d)
    return dates

def print_cal (dates, header=True, cols=True):
    dates = list(dates)
    dates_str = list("{0.day:-2} {0:%A}".format(d) for d in dates)
    zip_idx = len(dates) // 2 + 1
    if header:
        print(f'=== {"{0:%B} {0:%Y} ===".format(dates[0]).capitalize()}')
    if cols:
        for col in itertools.zip_longest(dates_str[:zip_idx], dates_str[zip_idx:], fillvalue=''):
            print(*col, sep='\t')
    else:
        print('\n'.join(dates_str))

def get_parsed (args=None):
    args = args or sys.argv[1:]
    now = datetime.datetime.now()
    parser = argparse.ArgumentParser(description='print the days of the given month and year')
    parser.add_argument('-c', '--columnate',
                        dest='cols', action='store_true',
                        help='columnate output.')
    parser.add_argument('-H', '--header',
                        dest='header', action='store_true',
                        help='print an header line with month and year.')
    parser.add_argument('-m', '--month',
                        dest='month', type=int, default=now.month,
                        help='set the month, default to the current month.')
    parser.add_argument('-y', '--year',
                        dest='year', type=int, default=now.year,
                        help='set the year, default to the current year.')
    parsed = parser.parse_args(args)
    if parsed.month not in range(1, 13):
        parser.error('month must be in range 1..12')
    return parsed

if __name__ == '__main__':
    args = get_parsed()
    print_cal(make_cal(args.year, args.month), args.header, args.cols)
