#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Name: get_deps
# Version: 0.1
# Author: Marco Chieppa ( a.k.a. crap0101 )
# Last Update: 2012-06-02
# Description: retrieve packages dependencies for apt-based distro
# Requirement: Python >= 2.7

# Copyright (C) 2012  Marco Chieppa (aka crap0101)

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

import apt
import argparse
import logging
import os
import sys

LOGNAME = 'get_deps'
LOG_LEVELS = ('DEBUG', 'INFO', 'WARNING', 'ERROR')
DEFAULT_LOG_LEVEL = 'INFO'
PRIORITIES = ('required', 'important', 'standard', 'optional', 'extra')

def get_pkg_deps (pkgname, priorities=(), cache=None):
    """
    pkgname: the package name
    priorities: a sequence of priorities names as strings (default: ())
    cache: an apt.Cache object (default: None)
    .
    Returns a set of depencencies for pkgname, excluding those packages
    which the priority attribute falls into the priorities argument.
    Raise IndexError if pkgname is not found in the cache.
    """
    if cache is None:
        cache = apt.Cache()
    pkg = cache[pkgname]
    pkg_deps = set()
    for dep in pkg.candidateDependencies:
        # first choice for multiple packages dep
        pkg_deps.add(dep.or_dependencies[0].name)
        # all of or_*
        #pkg_deps.update(odep.name for odep in dep.or_dependencies)
    if priorities:
        return set(p for p in pkg_deps if cache[p].priority not in priorities)
    else:
        return pkg_deps

def get_pkg_deep_deps (pgkname, priorities=(), cache=None):
    """
    pkgname: the package name
    priorities: a sequence of priorities names as strings (default: ())
    cache: an apt.Cache object (default: None)
    .
    Returns a set of depencencies for pkgname, excluding those packages
    which the priority attribute falls into the priorities argument.
    This function performs an in-deep search finding the pkgname
    dependencies and all the sub-dependencies.
    """
    if cache is None:
        cache = apt.Cache()
    pkg_ddeps = set()
    to_find = [pkgname]
    while True:
        nexts = set()
        for p in to_find:
            try:
                _pkgs = get_pkg_deps(p, priorities, cache)
                new_pkgs = _pkgs.difference(pkg_ddeps)
                pkg_ddeps.update(new_pkgs)
                nexts.update(new_pkgs)
            except KeyError as err:
                logging.getLogger(LOGNAME).warning(err)
        if nexts:
            to_find = list(nexts)
        else:
            break
    return pkg_ddeps

def get_deps (pkgname, priorities=(), cache=None, deep_search=False):
    """
    pkgname: the package name
    priorities: a sequence of priorities names as strings (default: ())
    cache: an apt.Cache object (default: None)
    deep_search: boolean flag (performing or not a deep search)
    .
    Returns pkgname dependencies using the functions get_pkg_deps or
    get_pkg_deep_deps in accordance to the deep_search flag.
    """
    if deep_search:
        return get_pkg_deep_deps(pkgname, priorities, cache)
    else:
        try:
            return get_pkg_deps(pkgname, priorities, cache)
        except KeyError as err:
            logging.getLogger(LOGNAME).warning(err)
            return set()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('packages',
        default=[], nargs='*', metavar='package_name',
        help='find deps for every package')
    parser.add_argument('-e', '--exclude-priority',
        dest='exclude_priorities', default=(), nargs='+', choices=PRIORITIES,
        metavar='NAME', help='''exclude dependencies with certain priority.
        Choices: %(choices)s.''')
    parser.add_argument('-d', '--deep',
        dest='deep', action='store_true', help='deep search dependencies')
    parser.add_argument('-l', '--log-level',
        dest='loglevel', metavar='LEVEL',
        choices=LOG_LEVELS, default=DEFAULT_LOG_LEVEL,
        help='set logging level: one of %(choices)s; default to %(default)s')
    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel)
    logger = logging.getLogger(LOGNAME)
    for pkgname in args.packages:
        deps = get_deps(pkgname, args.exclude_priorities, None, args.deep)
        logger.info("Package {what} depends on {num} packages:".format(
            what=pkgname, num=len(deps)))
        if deps:
            print ' '.join(sorted(deps))
