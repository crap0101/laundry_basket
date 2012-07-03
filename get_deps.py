import apt
import argparse
import logging
import os
import sys

LOGNAME = 'get_deps'
LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
DEFAULT_LOG_LEVEL = 'INFO'

def get_deps (pkgname, cache=None):
    if cache is None:
        cache = apt.Cache()
    try:
        pkg = cache[pkgname]
    except KeyError as err:
        logging.getLogger(LOGNAME).warning(err)
        return set()
    pkg_deps = set()
    for dep in pkg.candidateDependencies:
        # first choice for multiple packages dep
        pkg_deps.add(dep.or_dependencies[0].name)
        # all of or_*
        #pkg_deps.update(odep.name for odep in dep.or_dependencies)
    return pkg_deps

def get_deep_deps (pgkname, cache=None):
    if cache is None:
        cache = apt.Cache()
    pkg_ddeps = set()
    to_find = [pkgname]
    while True:
        nexts = set()
        for p in to_find:
            _pkgs = get_deps(p, cache)
            new_pkgs = _pkgs.difference(pkg_ddeps)
            pkg_ddeps.update(new_pkgs)
            nexts.update(new_pkgs)
        if nexts:
            to_find = list(nexts)
        else:
            break
    return pkg_ddeps

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('packages',
        default=[], nargs='*', metavar='package_name',
        help='find deps for every package')
    parser.add_argument('-d', '--deep',
        dest='deep', action='store_true', help='deep search dependencies')
    parser.add_argument('-l', '--log-level',
        dest='loglevel', metavar='LEVEL',
        choices=LOG_LEVELS, default=DEFAULT_LOG_LEVEL,
        help='set logging level: one of %(choices)s; default to %(default)s')
    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel)
    logger = logging.getLogger(LOGNAME)
    func = get_deep_deps if args.deep else get_deps
    for pkgname in args.packages:
        deps = func(pkgname)
        logger.info("Package {what} depends on {num} packages:".format(
            what=pkgname, num=len(deps)))
        print ' '.join(sorted(deps))
