#!/usr/bin/env python

# PyOpenTerminalHere: caja/nautilus action to open a terminal in the selected directory
# Version: 0.5
# Copyright (C) 2009-2025  Marco Chieppa ( a.k.a. crap0101 )

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

"""
NOTE: for the caja-actions-config-tool use %u as parameter and %d for the working directory
NOTE: when multiple folder are selected, multiple terminals will be opened.

Optional config file, target: ~/.PyOpenTerminalHere.rc

Config file example (see python's configparser module doc if in doubt):

[DEFAULT]
term = mate-terminal
working_dir_opt = "--working-directory={}"

The {} will be replaced with the current working directory path (really!)

"""

import configparser
import os
import re
import shlex
import subprocess
import sys
import tempfile
import time
try:
    from urllib import unquote
except ImportError:
    from urllib.parse import unquote


CONFIG_OPTIONS = {
    'term': 'mate-terminal',
    'working_dir_opt': '--working-directory={}'
}


def die_bad (e=None):
    _, t = tempfile.mkstemp(text=True, prefix=f'PyOpenTerminalHere_{time.time()}__')
    with open(t, 'w') as tmpfile:
        tmpfile.write('{} dies bad in this sad {} {}'.format(
            sys.argv[0],
            time.strftime("%Y-%m-%-d at %H:%M:%S", time.localtime()),
            'for unknown reasons... but the command line was: {}'.format(sys.argv)
                if e is None else 'because of this: {}'.format(e)))


def read_config(config_file, mapping):
    config = configparser.ConfigParser()
    config.read([config_file])
    for key, value in mapping.items():
        try:
            mapping[key] = config.get('DEFAULT', key)
        except configparser.NoOptionError:
            pass


def open_terminal (term, working_dir_fmt):
    path_to_open = ''
    if sys.argv[1:]:
        path_to_open = re.split('^file://', unquote(sys.argv[1]), 1)[-1]
        if path_to_open.startswith("trash://"):
            trash = re.split('^trash://', unquote(sys.argv[1]), 1)[-1]
            if trash == '/':
                path_to_open = os.path.join(unquote(os.getenv("HOME")),
                                            '.local/share/Trash/files')
            else:
                # FUCK %5C !!!!!!!
                path_to_open = re.sub('\\\\', '/', re.split('^trash://', trash, 1)[-1])
        if os.path.isfile(path_to_open):
            path_to_open = os.path.dirname(path_to_open)
    else:
        path_to_open = os.getcwd()
    if not path_to_open:
        die_bad()
        sys.exit(2)
    proc = subprocess.run(shlex.split(f'{term} {working_dir_fmt.format(path_to_open)}'),
                          capture_output=True)
    if proc.returncode != 0:
        die_bad(proc.stderr)
        sys.exit(3)

if __name__ == '__main__':
    config_file = os.path.join(os.getenv('HOME'), '.PyOpenTerminalHere.rc')
    read_config(config_file, CONFIG_OPTIONS)
    try:
        open_terminal(CONFIG_OPTIONS['term'], CONFIG_OPTIONS['working_dir_opt'])
    except Exception as e:
        die_bad(e)
        sys.exit(1)
