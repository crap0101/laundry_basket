#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# makepylst - Python script to create multiple playlist (.m3u) files
# initial release: 2009
# version: 0.5
# date: 2023-10-01
# Copyright (C) 2009  Marco Chieppa ( a.k.a. crap0101)

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not see <http://www.gnu.org/licenses/> 

from collections.abc import Sequence
import os
import pathlib
import sys
from typing import TypeAlias, Final
import warnings

ok_magic = False
try:
    import magic
    ok_magic = True
except ImportError:
    import mimetypes
    mimetypes.init()
try:
    import mutagen
    ok_info = True
except:
    ok_info = False



Path_t :TypeAlias = pathlib.Path

HEADER :Final = "#EXTM3U"
EXTENSION :Final = '.m3u'
BUFF :Final = 4096
AUDIO_TYPE :Final = ['flac',  'x-flac',
                     'ogg', '.ogg',
                     'mp3', '.mp3', 'mpeg',
                     'wav', '.wav', 'x-wav']
WARN_TYPE = ('ignore', 'always', 'error')

VERSION = '0.5'
PROGNAME = 'mkpylst'
EPILOG = ('As said, if no PATHs are given, read data from stdin,'
          ' one file per line, saving the results in the current directory'
          ' or (if provided) in the DESTDIR directory, in a file'
          f' named "playlist_YYYY_MM_DD{EXTENSION}". In this case, the -r/'
          '--recursive option is ignored, the -R/--relative option should'
          ' be used with care.',
          'Nice to have modules:',
          'python-magic -> https://github.com/ahupp/python-magic',
          'mutagen -> https://github.com/quodlibet/mutagen')
DESCRIPTION = ('A barebone m3u ( https://en.wikipedia.org/wiki/M3U ) playlist creator.')

class MimeError(Exception):
    pass

def showwarning (message, cat, fn, lno, *a, **k):
    print(message, file=sys.stderr)
warnings.showwarning = showwarning

if ok_info:
    def get_length (path :Path_t|str) -> int:
        try:
            f = mutagen.File(path)
            return int(f.info.length)
        except mutagen.MutagenError as err:
            warnings.warn(f'* file <str(path)>: {err}')
            return -1
else:
    def get_length (*a, **k):
        """Fake func for track's duration."""
        return -1

def get_parser ():
    p = argparse.ArgumentParser(prog=PROGNAME,
                                formatter_class=argparse.RawDescriptionHelpFormatter,
                                description=DESCRIPTION,
                                epilog='\n'.join(EPILOG))
    p.add_argument('paths',
                   nargs='*',
                   help='make a playlist for each path. If no paths'
                   ' are specified, read a list of files from stdin and'
                   ' create the output file in the current directory.')
    p.add_argument('-o', '--outdir',
                   dest='out_dir', metavar='DESTDIR',
                   help='write playlist files in the directory %(metavar)s'
                   ' (default is to write each playlist in its directory).')
    p.add_argument('-r', '--recursive',
                   dest='recursive', action='store_true',
                   help='make playlist files for every subdirectory')
    p.add_argument('-R', '--relative',
                   dest='relative', action='store_true',
                   help='write relative paths instead of absolute ones.')
    p.add_argument('-v', '--version',
                   action='version', version=f'%(prog)s {VERSION}')
    p.add_argument('-w', '--warn',
                   dest='warn_type', choices=WARN_TYPE, default=WARN_TYPE[0],
                   help="If set to 'ignore' no message is displayed, if 'always'"
                   " print messagges about skipped or unhandled files, when set"
                   " to 'error' turns warnings into exceptions. Default: '%(default)s'.")
    return p

def resolve_path (path :str|Path_t, strict=True) -> Path_t:
    """Returns a fully resolved Path object  giving a string or another Path.
    Can raise a FileNotFoundError or a RuntimeError."""
    if isinstance(path, str):
        return pathlib.Path.expanduser(pathlib.Path(path)).resolve(strict)
    return pathlib.Path.expanduser(path).resolve(strict)

def find (path :str|Path_t) -> list[Path_t]:
    """Returns a list of subdirectories under $path."""
    dirs = []
    for _dir, subdirs, files in os.walk(path):
        for d in subdirs:
            dirs.append(resolve_path(_dir).joinpath(d).resolve())
    return dirs

def check_mime_magic (filepath :Path_t) -> (str|bool, bool|Exception):
    """Checks $filepath's mime type using the magic mime module."""
    ## Changed to avoid warnings about compatibily mode:
    ## «Using compatibility mode with libmagic's python binding.
    ## See https://github.com/ahupp/python-magic/blob/master/COMPAT.md»
    #mime_magic = magic.open(magic.MAGIC_MIME)
    #mime_magic.load()
    _err = '?'
    try:
        fo = open(filepath, "rb")
        #info = mime_magic.buffer(fo.read(BUFF))
        info = magic.from_buffer(fo.read(BUFF), mime=True)
    except (FileNotFoundError, OSError) as err:
        _err = err
        return False, err # well, never returns
    finally:
        try:fo.close()
        except UnboundLocalError: return False, _err
    return info.split("/")[1].strip().lower(), False

def check_mime_mimetypes (filepath :Path_t) -> (str|bool, bool|Exception):
    """Checks $filepath's mime type using the mimetypes module."""
    try:
        return mimetypes.guess_type(filepath)[0].split('/')[1].strip().lower(), False
    except AttributeError as err:
        return False, err

def check_mime (filepath :Path_t) -> str:
    """Checks $filepath's mime type. Returns the associated identifing string.
    On errors, raise a MimeError."""
    m, err = _check_mime(filepath)
    if m == False:
        raise MimeError(err)
    return m

def get_paths (dirlist :Sequence[Path_t], recursive :bool):
    dirs = list(dirlist)
    if recursive:
        for d in dirlist:
            dirs.extend(find(d))
    return dirs

def filter_mime (files :Sequence[Path_t]) -> Sequence[Path_t]:
    res = []
    for f in files:
        try:
            filetype = check_mime(f)
        except MimeError as err:
            warnings.warn(f'ERROR: mime check on <{f.name}>: {err}')
        if filetype in AUDIO_TYPE:
            res.append(f)
        else:
            warnings.warn(f'* skipping {str(f)} (type: {filetype})')
    return res

def make_playlist (path :Path_t, destination :None|Path_t = None, relative :bool = False) -> None:
    files = list(path.joinpath(f) for f in path.iterdir() if f.is_file())
    playlist_name = f'{path.name}{EXTENSION}'
    if destination is None:
        outpath = path.joinpath(playlist_name)
    else:
        outpath = destination.joinpath(playlist_name)
    toplay = filter_mime(files)
    write_playlist(toplay, outpath, relative)

def write_playlist (paths :Sequence[Path_t], outpath :Path_t, relative :bool):
    if paths:
        with outpath.open('w') as p:
            p.write("#EXTM3U\n\n")
            for track in sorted(paths):
                length = get_length(track)
                p.write(f"#EXTINF:{length},{track.stem}\n") 
                p.write(f"{track.name}\n\n" if relative else f"{str(track)}\n\n")
    else:
        warnings.warn('* No suitable files founds!')


if __name__ == '__main__':
    import argparse
    import datetime
    parser = get_parser()
    args = parser.parse_args()
    _check_mime = check_mime_magic if ok_magic else check_mime_mimetypes
    if args.out_dir:
        args.out_dir = resolve_path(args.out_dir)
        if not args.out_dir.is_dir():
            parser.error(f'ERROR: {args.out_dir.name}: not a directory')
    if not args.paths:
        file_paths = []
        for line in sys.stdin:
            p = resolve_path(line.strip())
            if p.is_file():
                file_paths.append(p)
    else:
        args.paths = list(resolve_path(path) for path in args.paths)
        for path in args.paths:
            if not path.is_dir():
                parser.error(f'ERROR: {path.name}: not a directory')

    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', category=DeprecationWarning)
        warnings.simplefilter(args.warn_type)
        if not args.paths:
            name = datetime.date.strftime(datetime.datetime.now(), f"playlist_%Y-%m-%d{EXTENSION}")
            if not args.out_dir:
                args.out_dir = pathlib.Path().resolve().joinpath(name)
            else:
                args.out_dir = args.out_dir.joinpath(name)
            write_playlist(filter_mime(file_paths), args.out_dir, args.relative)
        else:
            for path in get_paths(args.paths, args.recursive):
                make_playlist(path, args.out_dir, args.relative)

