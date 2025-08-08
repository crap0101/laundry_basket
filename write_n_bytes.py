#!/usr/bin/python3

import array
import os

def write_bytes (num, out, fill=b'0'):
    add = b''
    m, r = divmod(num, len(fill))
    to_write = fill * m
    if r:
        to_write += fill[:r]
    arr = array.array('b', to_write)
    stream = open(out, 'wb') if isinstance(out, (str, bytes, os.PathLike)) else out
    with stream as f:
        arr.tofile(f)

if __name__ == '__main__':
    import sys
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--bytes-str',
                        dest='bytes_str', type=str,
                        default=b'0', metavar='BYTES_STRING',
                        help='fill FILE with %(metavar)s, default:"%(default)s."')
    parser.add_argument(dest='bytes_number', type=int, metavar='NUM',
                        help='fill FILE with %(metavar)s bytes.')
    parser.add_argument(dest='outfile', nargs='?', metavar='FILE',
                        type=argparse.FileType('wb'), default=sys.stdout.buffer,
                        help='write to %(metavar)s, defaul: %(default)s.')
    parsed = parser.parse_args()
    write_bytes(parsed.bytes_number, parsed.outfile, os.fsencode(parsed.bytes_str))


"""
crap0101@debian:~/test$ python 0.write_n_bytes.py 104 | wc -c
104
crap0101@debian:~/test$ python 0.write_n_bytes.py 104 foo -s 1abcZ
crap0101@debian:~/test$ ll foo
-rw-r--r-- 1 crap0101 crap0101 104 20 giu 23.23 foo
crap0101@debian:~/test$ cat foo;echo
1abcZ1abcZ1abcZ1abcZ1abcZ1abcZ1abcZ1abcZ1abcZ1abcZ1abcZ1abcZ1abcZ1abcZ1abcZ1abcZ1abcZ1abcZ1abcZ1abcZ1abc
"""
