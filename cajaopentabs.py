#!/usr/bin/env python3

"""
@author: Marco Chieppa | crap0101
@version: 0.2
@date: 2026-05-25

SYNOPSIS
    cajaopentabs.py FILE

DESCRIPTION
    Open caja tabs, reading paths from a file (one path per line).
    Consider only lines starting with '/'.
    Primarily intended to be used for startup applications in various DE.
"""
import os
import tempfile
import subprocess
import sys

cmd = ['caja', '-t']
with open(os.path.expanduser(sys.argv[1])) as f: # "~/0.cajaopentabs")) as f:
    for line in f:
        if line.startswith('/'):
            cmd.append(line.strip())

""" # test:
with tempfile.NamedTemporaryFile(mode='w', prefix='python-caja_', delete=0) as f:
    f.write(repr(cmd))
print(cmd)
"""
subprocess.run(cmd)
