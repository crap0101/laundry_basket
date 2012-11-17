#!/usr/bin/python
# -*- coding: UTF-8 -*-
# makepylst - Python script to create multiple playlist (.m3u) files
# version: 0.4
# date: 8 Jun 2009
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

class Playlist:

    def __init__(self, dirs, recursive=None, outf=None, magic_mime=None):
        self.count = 0
        self.dirs = dirs
        self.magic_mime = magic_mime
        self.recursive = recursive
        self.pwd = os.getcwd()
        self.outf = os.path.join(self.pwd, outf) if outf else False
        if self.outf:
            if not os.path.isdir(self.outf):
                print "ERRORE: la destinazione <%s> non esiste" % self.outf
                sys.exit(2)
            self.dirs.remove(outf) 
        self.AUDIO_TYPE = [
            'flac', 'FLAC',  'x-flac',
            'ogg', '.ogg', '.OGG', 'OGG',
            'mp3', '.MP3', 'mp3', 'MP3', 'mpeg',
            'wav', '.wav', '.WAV', 'WAV', 'x-wav'
        ]

    def find(self, path):
        lista_dirs = []
        for _dir, subdirs, files in os.walk(os.path.join(self.pwd, path)):
            for d in subdirs:
                lista_dirs.append(os.path.join(_dir, d))
        return lista_dirs

    def check_mime(self, file_):
        """controllo per tipo mime o estensione in assenza del modulo magic"""
        if self.magic_mime:
            mime_magic = magic.open(magic.MAGIC_MIME)
            mime_magic.load()
            try:
                file_to_read = open(file_, "r")
            except IOError:
                return False
            checked = mime_magic.buffer(file_to_read.read(4096))
            file_to_read.close()
            return checked.split("/")[1].strip()
        else:
            try:
                return mimetypes.guess_type(file_)[0].split('/')[1].strip()
            except AttributeError:
                return False
        return False

    def start(self):
        for d in self.dirs:
            if self.recursive:
                listdir = self.find(d)
                if not listdir:
                    try:
                        self.make(os.path.join(self.pwd, d))
                    except OSError:
                        print "salto <%s> non e un percorso valido" % d
                else:
                    for subd in listdir:
                        self.make(subd)
            else:
                try:
                    self.make(os.path.join(self.pwd, d))
                except OSError:
                    print "salto <%s> non e un percorso valido" % d

    def make(self, path):
        brani = os.listdir(path)
        name = os.path.basename(path)
        name = name if name else os.path.basename(path[:-1])
        playlist_name = "%s_playlist.m3u" % name
        toplay = []
        for brano in sorted(brani):
            filetype = self.check_mime(os.path.join(path, brano))
            if filetype not in self.AUDIO_TYPE:
                continue
            toplay.append(brano)
        if toplay:
            self.count += 1
            plst = open(os.path.join(
                self.outf if self.outf else path, playlist_name), "w"
            )
            plst.write("#EXTM3U\n\n")
            for track in toplay:
                #TODO aggiungere opzione per scrivere la lunghezza del file
                # (per quelli in cui si riesce a leggere) oppure lasciare -1
                plst.write("#EXTINF:-1,%s\n" % track) 
                plst.write("%s\n\n" % os.path.join(path, track))
            plst.close()


def info():
    print """
                ######  mkpylst  ######
Name: mkpylst: 
Description: a Python script to create multiple playlist (.m3u) files
Author: marco Chieppa ( a.k.a. crap0101 )
Version: 0.4
Date: 8 Jun 2009
License: GNU GPL v3 or later
"""
    sys.exit(1)

def help():
    print """
USO: 
  $ %s percorso_album [-R] [-o [percorso]]
OPZIONI:
  -R  > crea le playlist ricorsivamente per ogni sottocartella
        del percorso passato
  -o  percorso  > invece di creare le playlists nelle rispettive cartelle
                  le scrive in `percorso' 
""" % sys.argv[0]
    sys.exit(1)

if __name__ == '__main__':
    import os
    import sys
    ok_magic = True
    try:
        import magic
    except ImportError:
        import mimetypes
        mimetypes.init()
        ok_magic = False
    defopt = ["--default-yes", "-R", "-o", "-i", "--info", "-h", "--help"]
    dirs = set(sys.argv[1:]).difference(defopt)
    opts = set(sys.argv[1:]).difference(dirs)
    recursive = True if "-R" in opts else False
    outf = sys.argv[sys.argv[1:].index("-o") + 2] if "-o" in opts else False
    if "-h" in opts or "--help" in opts:
        help()
    if "-i" in opts or "--info" in opts:
        info()
    if not dirs or not sys.argv[1:]:
        help()
    create_playlist = Playlist(dirs, recursive, outf, ok_magic)
    create_playlist.start()
    print "fatto (%d files creati)" % create_playlist.count
