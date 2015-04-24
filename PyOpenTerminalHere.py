#!/usr/bin/env python

# PyOpenTerminalHere - open a terminal in the selected directory 
# Version: 0.3
# Usage: make it executable and paste in ~/.gnome2/nautilus-scripts
# Tested on GNOME nautilus 2.22.5.1, 3.4.2
# Non-essential requirement: Zenity

# Copyright (C) 2009-2015  Marco Chieppa ( a.k.a. crap0101 )

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

import os
import re
import sys
import urllib

def die_bad (strerr, prologue="Unable to open "):
    error_msg = [
        "zenity", 
        "--error", 
        "--text=%s '%s'" % (prologue, strerr)]
    os.execvp(error_msg[0], error_msg)

def open_terminal ():
    pattern = '^file://'
    path_to_open = False
    path_to_open = urllib.unquote(
        os.getenv("NAUTILUS_SCRIPT_SELECTED_FILE_PATHS", ''
            ).split("\n")[0].strip()
    )
    if not path_to_open or not os.path.isdir(path_to_open):
        path_to_open = os.getenv("NAUTILUS_SCRIPT_CURRENT_URI", '')
        if path_to_open.startswith("trash"):
            path_to_open = os.path.join(
                urllib.unquote(os.getenv("HOME")), '.local/share/Trash/files')
        else:
            try:
                path_to_open = urllib.unquote(
                    os.path.abspath(path_to_open.split(":")[1].strip()))
            except IndexError:
                path_to_open = ''
    if not path_to_open or not os.path.isdir(path_to_open):
        if sys.argv[1:]:
            path_to_open = re.split(pattern, sys.argv[1], maxsplit=1)[-1]
    if not path_to_open or not os.path.isdir(path_to_open):
        die_bad(path_to_open)
    cmd = ["gnome-terminal", '--working-directory=%s' % path_to_open]
    os.execvp(cmd[0], cmd)

if __name__ == '__main__':
    print sys.argv
    open_terminal()
    try:
        open_terminal()
    except Exception as e:
        die_bad(e, 'Unknown error:')
