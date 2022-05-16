#!/usr/bin/env python3
# >= 3.8.10

import argparse
from collections.abc import Sequence, Callable, Iterable
import functools
import itertools
import sys



######################
# utility class(es?) #
######################

class Injecretor:
    """Like an iterator, better than an iterator :-D
    0. can insert multiple value to be yielded while looping on it
    1. can retrieve the last yielded value (helpful in some circustances)
    """
    def __init__ (self, seq, name='noname', last=None):
        self._seq = iter(seq)
        self._next_vals = []
        self._last = last
        self._name = name
    @property
    def last (self):
        return self._last
    def __iter__ (self):
        return self
    def __next__(self):
        if self._next_vals:
            self._last = self._next_vals.pop(0)
            return self.last
        try:
            self._last = next(self._seq)
            return self.last
        except StopIteration:
            if self._next_vals:
                self._last = self._next_vals.pop(0)
                return self.last
            else:
                raise StopIteration
    def send (self, value):
        self._next_vals.append(value)


#####################
# utility functions #
#####################

def take (seq: Sequence, n: int) -> Iterable:
    """yields chunk of `n` items a times from `seq`"""
    it = iter(seq)
    while True:
        p = list(itertools.islice(it, 0, n))
        if not p:
            return
        yield p

def sort_two (seq: Sequence) -> Iterable:
    for lst in take(seq, 2):
        if len(lst) == 1:
            yield tuple(lst)
        else:
            a, b = lst
            yield (b,a) if a > b else (a, b)

def until_sort (seq: Sequence) -> Iterable:
    """yields items from `seq` grouped until sorted."""
    it = Injecretor(seq)
    lst = []
    while True:
        try:
            a = next(it)
            lst.append(a)
        except StopIteration:
            break
        for i in it:
            if i >= a:
                lst.append(i)
                a = i
            else:
                yield tuple(lst)
                lst = []
                it.send(i)
                break
    if lst:
        yield tuple(lst)


#####################
# Merging functions #
#####################

def merge_sorted (s1: Sequence, s2: Sequence) -> Sequence:
    """Merge two ordered sequences returning a third
    (paro paro from wikipedia ^L^)."""
    lst1 = list(s1)
    lst2 = list(s2)
    len1 = len(lst1)
    len2 = len(lst2)
    i1 = i2 = 0
    merged = []
    while i1 < len1 and i2 < len2:
        if lst1[i1] <= lst2[i2]:
            merged.append(lst1[i1])
            i1 += 1
        else:
            merged.append(lst2[i2])
            i2 += 1
    while i1 < len1:
        merged.append(lst1[i1])
        i1 += 1
    while i2 < len2:
        merged.append(lst2[i2])
        i2 += 1
    return merged

def merge_sorted_g (s1: Sequence, s2: Sequence) -> Iterable:
    """Merge two ordered sequences returning a third. Better."""
    g1 = Injecretor(s1,name='s1')
    g2 = Injecretor(s2,name='s2')
    for i, j in itertools.zip_longest(g1, g2, fillvalue=None):
        try:
            if i <= j:
                yield i
                g2.send(j)
            else:
                yield j
                g1.send(i)
        except TypeError:
            if i is None and j is None:
                return
            elif i is None:
                g2.send(j)
                break
            elif j is None:
                g1.send(i)
                break
            else:
                raise
    for i in g1:
        yield i
    for j in g2:
        yield j


########################
# Merge-sort functions #
########################

def merge_sort (seq: Sequence, func: Callable = merge_sorted_g) -> Sequence:
    """merge sort"""
    return list(functools.reduce(func, sort_two(seq)))


def merge_sort2 (seq: Sequence, func: Callable = merge_sorted_g) -> Sequence:
    """merge sort...take advantage from partial ordered seqs"""
    return list(functools.reduce(func, until_sort(seq)))


#########
# Tests #
#########

def _test_merged (func1, func2, shortl=None, longl=None):
    if shortl:
        for args in shortl:
            r1 = list(func1(*args))
            r2 = list(func2(*args))
            assert r1 == r2, 'ERR: {} != {}'.format(r1, r2)
        print('assert (merge) [short]: OK')
    if longl:
        for l1, l2 in longl:
            assert (list(sorted(list(l1)+list(l2)))
                    == list(merge_sorted(l1,l2))
                    == list(merge_sorted_g(l1, l2)))
        print('assert (merge) [long]: OK')

def _test_msort ():
    from random import randint as ri
    from random import shuffle
    lsts = [list(range(ri(-100,100),ri(100,200))) for _ in range(100)]
    for lst in lsts:
        shuffle(lst)
    for lst in lsts:
        s1 = list(merge_sort(lst))
        s2 = list(merge_sort(lst, func=merge_sorted))
        s3 = sorted(lst)
        s4 = list(merge_sort2(lst))
        assert s2 == s1, 'ERR (merge sort: merge_sorted <> merge_sorted_g): {} != {}'.format(s1, s2)
        assert s1 == s3, 'ERR (merge_sort <> builtin sorted): {} != {}'.format(s1, s3)
        assert s1 == s4, 'ERR (merge_sort <> merge_sort2): {} != {}'.format(s1, s4)
    print('assert (merge-sort): OK')

def _test (*in_args, debug=False, stats=False):
    from collections import namedtuple as np
    from enum import Enum
    from math import nan
    from random import randint as ri
    import timeit
    Config = np('Config',
                '        min     max    len   repeat',
                defaults=(-10000, 10000, 1001, 100    ))
    c = Config()
    funcs = 'merge_sorted merge_sorted_g'.split()
    setup = 'from __main__ import {}'.format(','.join(funcs))
    report  = 'function {:20} {:.6}s'
    # pair two by two
    lsts = tuple(itertools.zip_longest(
        *[iter(range(*sorted((ri(c.min, c.max),ri(c.min, c.max))))
               for i in range(c.len))]*2, fillvalue=()))
    if debug:
        print('\n'.join(
            ' | '.join(f'len:{len(l):<5} min:{min(l,default=nan):<5} max:{max(l,default=nan):<5}'
                       for l in pair)
            for pair in lsts))
        for pair in lsts:
            for l in pair:
                assert list(l) == list(sorted(l))
        print('assert (sorted input): OK')
    if stats:
        print('***Some stats:')
        print('{} list pairs'.format(len(lsts)))
        for f, fname in [(min, 'min value'), (max, 'max value')]:
            r = functools.reduce(f, itertools.chain(*itertools.chain.from_iterable(lsts)))
            print('lists {}: {:-5}'.format(fname, r))
        llen = tuple(map(len,itertools.chain.from_iterable(lsts)))
        print('Longer list:  {:-10} items'.format(max(llen)))
        print('Shorter list: {:-10} items'.format(min(llen)))
        print('average length: {:.2f}'.format(sum(llen)/len(llen)))
    # test merging
    print('*** Test merging...')
    for a in in_args:
        _test_merged(merge_sorted, merge_sorted_g, shortl=a)
    _test_merged(merge_sorted, merge_sorted_g, longl=lsts)
    _test_msort()
    print('*** Time tests config: {}'.format(
        ' | '.join('{}: {}'.format(*item) for item in c._asdict().items())))
    # test merging time
    print('*** Merging times...')
    for f in funcs:
        stmt = 'for pair in lsts: {}(*pair)'.format(f)
        t  = timeit.Timer(stmt=stmt, setup=setup, globals=locals()).timeit(c.repeat)
        print(report.format(f'{f}:', t/c.repeat))
    # test sorting time
    print('*** Sorting times...')
    rands = [list(range(ri(-100,100),ri(100,200))) for _ in range(100)]
    # merge_sort
    stmt = 'for l in rands: list(merge_sort(l))'
    t  = timeit.Timer(stmt=stmt, setup='from __main__ import merge_sort', globals=locals()).timeit(c.repeat)
    print(report.format('merge_sort:', t/c.repeat))
    # merge_sort2
    stmt = 'for l in rands: list(merge_sort2(l))'
    t  = timeit.Timer(stmt=stmt, setup='from __main__ import merge_sort2', globals=locals()).timeit(c.repeat)
    print(report.format('merge_sort2:', t/c.repeat))
    # builtin sorted
    stmt = 'for l in rands: sorted(l)'
    t  = timeit.Timer(stmt=stmt, globals=locals()).timeit(c.repeat)
    print(report.format('(builtin) sorted:', t/c.repeat))



def get_parsed():
    p = argparse.ArgumentParser()
    p.add_argument('-t', '--test-time', dest='test_time', action='store_true', help='test time')
    p.add_argument('-T', '--test-functions', dest='test_funcs', action='store_true', help='test functions')
    p.add_argument('-q', '--quit', dest='quit', action='store_true', help='quit after tests')
    p.add_argument('-d', '--debug', dest='debug', action='store_true', help='print debug info (tests only)')
    p.add_argument('-s', '--stats', dest='stats', action='store_true', help='print some stat (tests only)')
    return p.parse_args()


if __name__ == '__main__':
    inputs = [([],[]), ([], range(5)), (range(9),[]),
        (range(10), range(5,15)),
        (range(6,12), range(5)),
        (range(10), range(2,6)),
        (range(2,6), range(10)),
        (range(1), range(1,2)),
    ]
    p = get_parsed()
    if p.test_time:
        _test(inputs, debug=p.debug, stats=p.stats)
        if p.quit:
            sys.exit(0)
    # brief example
    for lsts in inputs:
        print('------\n[MS]  input: {0[0]} {0[1]} -> {1}'.format(
            lsts, merge_sorted(*lsts)))
        print('[MSG] input: {0[0]} {0[1]} -> {1}'.format(
            lsts, list(merge_sorted_g(*lsts))))


"""
crap0101@orange:~/test$ python3 merge-sort+Injecretor.py -tqds
[... long long output omitted ...]
len:14145 min:-7655 max:6489  | len:2594  min:2179  max:4772 
len:7657  min:-6881 max:775   | len:3038  min:-2241 max:796  
len:59    min:4820  max:4878  | len:10363 min:-5098 max:5264 
len:4849  min:-6714 max:-1866 | len:8819  min:-170  max:8648 
len:6981  min:1020  max:8000  | len:13615 min:-7817 max:5797 
len:6342  min:-5798 max:543   | len:269   min:-8400 max:-8132
len:10064 min:-760  max:9303  | len:10878 min:-5139 max:5738 
len:1363  min:8170  max:9532  | len:2252  min:295   max:2546 
len:4614  min:-1568 max:3045  | len:15678 min:-8133 max:7544 
len:10106 min:-9078 max:1027  | len:17151 min:-9824 max:7326 
len:11610 min:-3794 max:7815  | len:2981  min:-1692 max:1288 
len:12577 min:-5315 max:7261  | len:2460  min:-2752 max:-293 
len:16540 min:-9637 max:6902  | len:0     min:nan   max:nan  
assert (sorted input): OK
***Some stats:
501 list pairs
lists min value: -9996
lists max value:  9999
Longer list:       19033 items
Shorter list:          0 items
average length: 6647.49
*** Test merging...
assert (merge) [short]: OK
assert (merge) [long]: OK
assert (merge-sort): OK
*** Time tests config: min: -10000 | max: 10000 | len: 1001 | repeat: 100
*** Merging times...
function merge_sorted:        2.14101s
function merge_sorted_g:      0.000149758s
*** Sorting times...
function merge_sort:          1.1304s
function merge_sort2:         0.00946821s
function (builtin) sorted:    0.000196011s

crap0101@orange:~/test$ python3  merge-sorted+Injecretor__test-time.py 
------
[MS]  input: [] [] -> []
[MSG] input: [] [] -> []
------
[MS]  input: [] range(0, 5) -> [0, 1, 2, 3, 4]
[MSG] input: [] range(0, 5) -> [0, 1, 2, 3, 4]
------
[MS]  input: range(0, 9) [] -> [0, 1, 2, 3, 4, 5, 6, 7, 8]
[MSG] input: range(0, 9) [] -> [0, 1, 2, 3, 4, 5, 6, 7, 8]
------
[MS]  input: range(0, 10) range(5, 15) -> [0, 1, 2, 3, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 11, 12, 13, 14]
[MSG] input: range(0, 10) range(5, 15) -> [0, 1, 2, 3, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 11, 12, 13, 14]
------
[MS]  input: range(6, 12) range(0, 5) -> [0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11]
[MSG] input: range(6, 12) range(0, 5) -> [0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11]
------
[MS]  input: range(0, 10) range(2, 6) -> [0, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 7, 8, 9]
[MSG] input: range(0, 10) range(2, 6) -> [0, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 7, 8, 9]
------
[MS]  input: range(2, 6) range(0, 10) -> [0, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 7, 8, 9]
[MSG] input: range(2, 6) range(0, 10) -> [0, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 7, 8, 9]

"""
