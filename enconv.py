#!/usr/bin/env python

# Copyright (c) 2024  Marco Chieppa | crap0101

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

PROGNAME = 'enconv'
VERSION = '0.1'

__doc__ = f"""
{PROGNAME} v{VERSION}
Changes the encoding of the input file (or stdin)
to a new encoding (default utf-8) and write the
result on a new file (or stdout).

Tested with: Python 3.10.12
Optional modules: chardet @ https://github.com/chardet/chardet
"""


import argparse
import codecs
from collections.abc import Iterator
import io
import sys
from typing import BinaryIO

# EXTERNAL, OPTIONAL IMPORT
try:
    import chardet
    from chardet.universaldetector import UniversalDetector
    HAVE_CHARDET = True
except ImportError:
    HAVE_CHARDET = False


def change_encoding(stream: BinaryIO,
                    input_enc='utf-8',
                    output_enc='utf-8',
                    chunk_size=1024) -> Iterator[bytes]:
    """
    Yields bytes from $stream after encoding it
    from $input_enc encoding to $output_enc encoding.
    """
    while (readed := stream.read(chunk_size)):
        yield readed.decode(input_enc).encode(output_enc)


def check_codec(codec_string: str) -> bool:
    """Returns True if $coded_string is a known codec."""
    try:
        return bool(codecs.lookup(codec_string))
    except LookupError:
        return False


def get_binstream(filename, mode='r'):
    """
    If $filename is already a compatible I/O stream,
    returns the underlying buffer, otherwise opens it
    in binary mode and returns the resulting file object.
    $mode must be 'r' for a reader or 'w' for a writer.
    """
    if mode not in set('rw'):
        raise ValueError(f'Unkown mode: <{mode}>')
    if isinstance(filename, io.IOBase):
        return filename.buffer
    return open(filename, mode=mode+'b')


def guess_encoding_bigfile(filename, chunk=1024):
    """
    Returns the encoding of $filename, or None if fails.
    Reads $chunk bytes of $filename at a time.
    """
    detect = UniversalDetector()
    with open(filename, mode='rb') as f:
        while (readed := f.read(chunk)):
            detect.feed(readed)
            if detect.done:
                break
    detect.close()
    return detect.result['encoding']

def guess_encoding_default(filename):
    """Returns the encoding of $filename, or None if fails."""
    with open(filename, mode='rb') as f:
        return chardet.detect(f.read())['encoding']


def get_parser():
    """Returns an argparse's parser object."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-b", '--bigfile',
                        dest="bigfile", action='store_true',
                        help='''Use a specific function (rather slower
                        but safer) to check the file's encoding,
                        trying to avoid memory errors.''')
    parser.add_argument("-c", '--check-enc-only',
                        dest="only_check_enc", action='store_true',
                        help="Prints the input file's encoding and exit.")
    parser.add_argument("-e", '--input-encoding',
                        dest="input_enc", default=None, metavar='ENC',
                        help='''input file encoding.
                        If not provided, tries to guess it.''')
    parser.add_argument("-E", "--output-encoding",
                        dest="output_enc", default='utf-8', metavar="ENC",
                        help='''output file encoding.
                        If not provided, uses %(default)s.''')
    parser.add_argument("-i", "--input-file",
                        dest="input_file", default=sys.stdin, metavar="FILE",
                        help="Path to a file, otherwise uses stdin.")
    parser.add_argument("-o", "--output-file",
                        dest="output_file", default=sys.stdout, metavar="FILE",
                        help="Path to a file, otherwise uses stdout.")
    parser.add_argument('-v', '--version',
                        action='version', version=f'{VERSION}')
    return parser
                          
if __name__ == '__main__':
    parser = get_parser()
    parsed = parser.parse_args()
    if parsed.bigfile:
        guess_encoding = guess_encoding_bigfile
    else:
        guess_encoding = guess_encoding_default
    if parsed.input_enc is None:
        if parsed.input_file is sys.stdin:
            parser.error("Using stdin as input requires "
                         "specify the input encoding.")
        elif not HAVE_CHARDET:
            parser.error("Can't guess input encoding, "
                         "specify it of install the chardet module.")
        parsed.input_enc = guess_encoding(parsed.input_file)
    if parsed.only_check_enc:
        print(parsed.input_enc)
        sys.exit(0)
    if parsed.input_enc is None:
        parser.error("Can't detect input file encoding")
    if not check_codec(parsed.input_enc):
        parser.error(f'Unknown input codec: {parsed.input_enc}')
    if not check_codec(parsed.output_enc):
        parser.error(f'Unknown output codec: {parsed.input_enc}')
    
    with get_binstream(parsed.input_file, mode='r') as fin:
        with get_binstream(parsed.output_file, mode='w') as fout:
            for data in change_encoding(
                    fin, parsed.input_enc, parsed.output_enc):
                fout.write(data)
