#!/usr/bin/python

# PyOpenTerminalHere - open a terminal in the selected directory 
# Version: 0.2
# Usage: make it executable and paste in ~/.gnome2/nautilus-scripts
# Tested on GNOME nautilus 2.22.5.1
# Non-essential requirement: Zenity

# Copyright (C) 2009  Marco Chieppa ( a.k.a. crap0101 )

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
import urllib

def open_terminal():
    path_to_open = False
    path_to_open = urllib.unquote(
        os.getenv("NAUTILUS_SCRIPT_SELECTED_FILE_PATHS", None
            ).split("\n")[0].strip()
    )
    if not path_to_open or not os.path.isdir(path_to_open):
        path_to_open = os.getenv("NAUTILUS_SCRIPT_CURRENT_URI", None)
        if path_to_open.startswith("trash"):
            path_to_open = os.path.join(
                urllib.unquote(os.getenv("HOME")), '.local/share/Trash/files')
        else:
            path_to_open = urllib.unquote(
                os.path.abspath(path_to_open.split(":")[1].strip()))
    if not path_to_open or not os.path.isdir(path_to_open):
        error_msg = [
            "zenity", 
            "--error", 
            "--text=non riesco ad aprire '%s'" % path_to_open
        ]
        os.execvp(error_msg[0], error_msg)
    cmd = ["x-terminal-emulator", '--working-directory=%s' % path_to_open]
    os.execvp(cmd[0], cmd)

if __name__ == '__main__':
    open_terminal()

