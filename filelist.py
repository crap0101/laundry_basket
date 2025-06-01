# author: Marco Chieppa
# year: 2025

from collections.abc import Iterable
from itertools import chain
import os
import sys

def dcount (depth):
    if depth == float('+inf'):
        def inner_count():
            while True:
                yield True
    else:
        def inner_count():
            #depth = depth
            level = 0
            while level < depth:
                level += 1
                yield True
    return inner_count

def find (path, depth=float('+inf')):
    """Yields pathnames starting from *path* descending *depth* levels.
    Level 0 is the level of *path*."""
    if depth < 0:
        raise ValueError("find: invalid *depth* value, must be >= 0")
    levels = [[path]]
    for _ in dcount(depth)():
        new_level = []
        for base in levels[-1]:
            with os.scandir(base) as dir_iter:
                for item in dir_iter:
                    if item.is_dir(follow_symlinks=False):
                        new_level.append(item.path)
        if not new_level:
            break
        levels.append(new_level)
    for dirname in chain(*levels):
        with os.scandir(dirname) as dir_iter:
            for item in dir_iter:
                if item.is_file():
                    yield item.path


if __name__ == '__main__':
    for p in find(sys.argv[1], float(sys.argv[2])):
        print(p)
