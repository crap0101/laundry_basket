#!/usr/bin/env python

__doc__ = '''
Read and extract data from the NETGEAR DG834Gv5 cfg file.
(To check if working with other routers)
At this time, it extract 
'''

from collections import defaultdict
from io import BufferedReader
import os
from pathlib import Path
import sys

def get_data (path: (str|bytes|Path|BufferedReader), mode: str ='rb') -> bytes:
    if isinstance(path, BufferedReader):
        return path.read()
    with open(path, mode) as data:
        return data.read()

def read_cfg (path: (str|bytes|Path|BufferedReader), mode: str ='rb') -> bytes:
    return get_data(path, mode)

def data_filter (data: bytes, field_sep: bytes) -> list:
    datamap = defaultdict(list)
    trash = []
    dataseq = data.split(field_sep)
    for item in dataseq:
        if item:
            try:
                key, value = item.split(b'=')
                datamap[key].append(value)
            except ValueError as e:
                trash.append(item)
    return datamap, trash

def decode_map (datamap, encoding='ascii'):
    encoded_map = dict()
    for k, v in datamap.items():
        values = list(i.decode(encoding) for i in v)
        encoded_map[k.decode(encoding)] = values
    return encoded_map

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.register('type', 'hexadecimal', lambda s: bytes.fromhex(s))
    parser.add_argument('-s', '--field-separator',
                        dest='field_sep', type='hexadecimal', default=b'\0',
                        help="configuration's items separator, as hexadecimal number. Default: %(default)s")
    parser.add_argument('-S', '--sort',
                        dest='sort', action='store_true',
                        help='print the key/value pairs sorted by name')
    trashgroup = parser.add_mutually_exclusive_group()
    trashgroup.add_argument('-t', '--trash',
                            dest='trash', action='store_true',
                            help='display trashed items too, one per line.')
    trashgroup.add_argument('-T', '--only-trash',
                            dest='only_trash', action='store_true',
                            help='display trashed items, one per line.')
    parser.add_argument('path',
                        metavar='PATH', nargs="?", default=sys.stdin.buffer,
                        help='Path to the cfg file, default is to read from stdin.')

    parsed = parser.parse_args()
    data = read_cfg(parsed.path)
    datamap, trash = data_filter(data, parsed.field_sep)
    if parsed.only_trash:
        for t in trash:
            print(t)
    else:
        datamap = decode_map(datamap)
        _sort = lambda d: dict(sorted(d.items())) if parsed.sort else d
        for k,v in _sort(datamap).items():
            print(k, "=", ','.join(v))
        if parsed.trash:
            print(f'{"="*50}\nTRASH:\n{"="*50}')
            for t in trash:
                print(t)
