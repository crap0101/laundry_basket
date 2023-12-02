#
# author: Marco Chieppa | crap0101
#

"""
quick-and-dirty script for discussions download 
Cfr. http://forum.ubuntu-it.org/viewtopic.php?f=32&t=540361
"""


import argparse
import os
import re
import sys
import tempfile

import mechanize


def _get_args(args=None):
    p = argparse.ArgumentParser()
    p.add_argument('url',
                   metavar='URL', help='download topic from %(metavar)s')
    p.add_argument('-d', '--output-dir',
                   metavar='PATH', default=tempfile.gettempdir(),
                   dest='out', help='put files in %(metavar)s')
    return p.parse_args(args)

def save (data, filename):
    with open(filename, 'w') as out:
        out.write(data)

def get_topic (url):
    """Yield the topic from `url` one page at a time."""
    br = mechanize.Browser()
    br.open(url)
    while True:
        print_page = list(br.links(url_regex='.*print$'))
        if not print_page:
            print("skipping %s: no print page!" % br.response().geturl())
        else:
            resp = br.follow_link(print_page[0])
            yield resp.get_data()
            br.back()
        next_page = list(br.links(url_regex='.*start=\d+$', text='Successiva'))
        if not next_page:
            break
        else:
            br.follow_link(next_page[0])

if __name__ == '__main__':
    args = _get_args()
    fmtfile = os.path.join(args.out, "%03d.html")
    for n, data in enumerate(get_topic(args.url), start=1):
        save(data, fmtfile % n)
