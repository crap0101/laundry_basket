#!/usr/bin/env python3
# >= 3.8.10

import argparse
import collections 
from collections.abc import Sequence, Callable, Iterable
import functools
import itertools
import sys
import time


###################
# utility classes #
###################


class Config:
    def __new__ (cls, **k):
        inst = super().__new__(cls)
        inst.fields = ('min', 'max', 'len', 'repeat')
        inst.defvalues = (-10000, 10000, 1001, 1000)
        for k,v in zip(inst.fields, inst.defvalues):
            setattr(inst, k, v)
        return inst
    def __init__ (self, **kw):
        for k, v in kw.items():
            self.__setitem__(k, v)
    def __setitem__ (self, k, v):
        if k not in self.fields:
            raise KeyError(k)
        setattr(self, k, v)
    def as_dict (self):
        return dict((attr, getattr(self, attr)) for attr in self.fields)


class Injecretor:
    """Like an iterator, better than an iterator :-D
    0. can insert multiple value to be yielded while looping on it.
    1. can retrieve the last yielded value (helpful in some circustances).
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

def timer (f):
    def inner (*a, **k):
        ts = time.time()
        ret = f(*a, **k)
        t = time.time() - ts
        print(f'{f.__name__} runs in: {t:.4f} seconds')
        return ret
    return inner

def group_sort (seq: Sequence) -> Sequence:
    """Returns items from `seq` grouped while sorted."""
    slst = []
    lst = []
    it = iter(seq)
    try:
        a = next(it)
        lst.append(a)
    except StopIteration:
        return slst
    for i in it:
        if i >= a:
            lst.append(i)
            a = i
        else:
            slst.append(lst)
            a = i
            lst = [a]
    if lst:
        slst.append(lst)
    return slst

def group_sort2 (seq: Sequence) -> Sequence:
    """Returns items from `seq` grouped while sorted."""
    slst = []
    it, it2 = itertools.tee(seq, 2)
    pidx = 0
    try:
        a = next(it)
    except StopIteration:
        return slst
    for idx, i in enumerate(it, 1):
        if i >= a:
            a = i
        else:
            slst.append(list(itertools.islice(it2, idx-pidx)))
            a = i
            pidx = idx
    last = list(itertools.islice(it2, idx-pidx+1))
    if last:
        slst.append(last)
    return slst

def reduce(func, seq, init=None):
    it = iter(seq)
    if init is None:
        val = next(it)
    else:
        val = init
    for i in it:
        val = func(val, i)
    return val

def sort_two (seq: Sequence) -> Sequence:
    """Return sorted seqs of items, two by two."""
    pairs = []
    for lst in takes(seq, 2):
        if len(lst) == 1:
            pairs.append(tuple(lst))
        else:
            a, b = lst
            pairs.append((b,a) if a > b else (a, b))
    return pairs

def takes (seq: Sequence, n: int) -> Iterable:
    """Yields chunk of `n` items a times from `seq`"""
    it = iter(seq)
    while True:
        p = list(itertools.islice(it, 0, n))
        if not p:
            return
        yield p

def until_sorti (seq: Sequence) -> Iterable:
    """Yields items from `seq` grouped until sorted."""
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

def zip_2 (s1, s2, fillvalue=None):
    """Returns pairs of item form `s1` and `s2`,
    Stops at the end of the shorter seq, missing
    value will be replaced by `fillvalue`.
    """
    is1 = iter(s1)
    is2 = iter(s2)
    while True:
        ret = []
        try:
            v1 = next(is1)
            ret.append(v1)
        except StopIteration:
            ret.append(None)
        try:
            v2 = next(is2)
            ret.append(v2)
        except StopIteration:
            ret.append(None)
        yield tuple(ret)
        if None in ret:
            return


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


def merge_sorted_c (s1: Sequence, s2: Sequence) -> Iterable:
    """Merge two ordered sequences returning a third. Better.
    """
    merged = collections.deque()
    g1 = Injecretor(s1,name='s1')
    g2 = Injecretor(s2,name='s2')
    for c in itertools.count(1):
        try:
            i = next(g1)
        except StopIteration:
            i = None
        try:
            j = next(g2)
        except StopIteration:
            j = None
        try:
            #print(c)
            if i <= j:
                merged.append(i)
                g2.send(j)
            else:
                merged.append(j)
                g1.send(i)
        except TypeError:
            if i is None and j is None:
                break
            elif i is None:
                g2.send(j)
                for j in g2:
                    merged.append(j)
                    c += 1
                break
            elif j is None:
                g1.send(i)
                for i in g1:
                    merged.append(i)
                    c += 1
                break
            else:
                raise
    return merged


def merge_sorted_g (s1: Sequence, s2: Sequence) -> Sequence:
    """Merge two ordered sequences returning a third. Better?...slower o.O ."""
    g1 = Injecretor(s1,name='s1')
    g2 = Injecretor(s2,name='s2')
    merged = []
    for i, j in itertools.zip_longest(g1, g2, fillvalue=None): #zip_2(g1, g2): 
        try:
            if i <= j:
                merged.append(i)
                g2.send(j)
            else:
                merged.append(j)
                g1.send(i)
        except TypeError:
            if i is None and j is None:
                break
            elif i is None:
                g2.send(j)
                break
            elif j is None:
                g1.send(i)
                break
            else:
                raise
    for i in g1:
        merged.append(i)
    for j in g2:
        merged.append(j)
    return merged

def merge_sorted_i (s1: Sequence, s2: Sequence) -> Iterable:
    """Merge two ordered sequences, returns an iterator."""
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
    """Merge-sort."""
    reduce = functools.reduce
    return list(reduce(func, sort_two(seq), []))


def merge_sort2 (seq: Sequence, func: Callable = merge_sorted_g) -> Sequence:
    """Merge-sort... take advantage from partial ordered seqs."""
    reduce = functools.reduce
    return list(reduce(func, group_sort(seq), []))

def merge_sort3 (seq: Sequence, func: Callable = merge_sorted_i) -> Sequence:
    """merge sort...take advantage from partial ordered seqs"""
    d = collections.deque(group_sort(seq))
    if not d:
        return []
    while len(d) > 1:
        a = d.pop()
        b = d.pop()
        d.appendleft(func(a, b))
    assert len(d) == 1
    return d.pop()


#########
# Tests #
#########

def _test_iter (seqs):
    for s in seqs:
        it = Injecretor(s)
        for i in it:
            pass
    print('test Injecretor: OK')

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
        s1 = list(merge_sort(lst, func=merge_sorted))
        s2 = list(merge_sort(lst, func=merge_sorted_g))
        s3 = list(merge_sort(lst, func=merge_sorted_c))
        s4 = list(merge_sort2(lst))
        s5 = list(merge_sort2(lst, func=merge_sorted_c))
        s6 = sorted(lst)
        assert s1 == s2, 'ERR (merge sort: merge_sorted <> merge_sorted_g): {} != {}'.format(s1, s2)
        assert s1 == s3, 'ERR (merge_sort: merge_sorted <> merge_sorted_c): {} != {}'.format(s1, s3)
        assert s1 == s4, 'ERR (merge_sort <> merge_sort2 (merge_sorted_g)): {} != {}'.format(s1, s4)
        assert s1 == s5, 'ERR (merge_sort <> merge_sort2 (merge_sorted_c)): {} != {}'.format(s1, s5)
        assert s1 == s6, 'ERR (merge_sort <> builtin sorted): {} != {}'.format(s1, s6)
    print('assert (merge-sort): OK')

@timer
def _test (config, *in_args, test_time=False, test_funcs=False, debug=False, stats=False):
    from enum import Enum
    from itertools import chain
    ichain = chain.from_iterable
    from math import nan
    from random import randint as ri
    from random import shuffle
    import timeit
    c = config
    funcs_s = 'merge_sorted merge_sorted_c merge_sorted_g merge_sorted_i'.split()
    setup = 'from __main__ import {}'.format(','.join(funcs_s))
    report  = 'function {:20} {:.6}s'
    # pair two by two, sorted lists
    lsts = tuple(itertools.zip_longest(
        *[list(range(*sorted((ri(c.min, c.max),ri(c.min, c.max))))
               for i in range(c.len))]*2, fillvalue=()))
    # unsorted lists
    lstr = []
    for pair in lsts:
        r1, r2 = map(list, pair)
        shuffle(r1)
        shuffle(r2)
        lstr.append((r1,r2))
    if debug:
        print('\n'.join(
            ' | '.join(f'len:{len(l):<5} min:{min(l,default=nan):<5} max:{max(l,default=nan):<5}'
                       for l in pair)
            for pair in lsts))
        for pair in lsts:
            for l in pair:
                assert list(l) == list(sorted(l))
        print('assert (sorted input): OK')
    if test_funcs:
        ################
        # test iteration
        _test_iter(ichain(lstr))
        print('*** Test merging...')
        for a in in_args:
            ###############
            # test merging
            _test_merged(merge_sorted, merge_sorted_g, shortl=a)
            _test_merged(merge_sorted_g, merge_sorted_c, shortl=a)
            _test_msort()
        ###########################
        # test grouping and sorting
        for l in ichain(lstr[:5]):
            assert group_sort(l) == group_sort2(l)
        print('assert (group_sort*): OK')
        stmt = 'for l in ichain(lstr[:10]): list(sort_two(l))'
        t  = timeit.Timer(stmt=stmt, setup='from __main__ import sort_two', globals=locals()).timeit(c.repeat)
        print(report.format('sort_two:', t/c.repeat))
        stmt = 'for l in ichain(lstr[:10]): list(group_sort(l))'
        t  = timeit.Timer(stmt=stmt, setup='from __main__ import group_sort', globals=locals()).timeit(c.repeat)
        print(report.format('group_sort:', t/c.repeat))
        stmt = 'for l in ichain(lstr[:10]): list(group_sort2(l))'
        t  = timeit.Timer(stmt=stmt, setup='from __main__ import group_sort2', globals=locals()).timeit(c.repeat)
        print(report.format('group_sort2:', t/c.repeat))
    if stats:
        print('***Some stats (merging):')
        print('list pairs: {:-10}'.format(len(lsts)))
        for f, fname in [(min, 'min value'), (max, 'max value')]:
            r = functools.reduce(f, itertools.chain(*itertools.chain.from_iterable(lsts)), 0)
            print('lists {}: {:-10}'.format(fname, r))
        llen = tuple(map(len,itertools.chain.from_iterable(lsts)))
        print('Longer list:    {:-10} items'.format(max(llen)))
        print('Shorter list:   {:-10} items'.format(min(llen)))
        print('average length: {:-10.2f}'.format(sum(llen)/len(llen)))
        print('Total items:    {:-10}'.format(sum(llen)))
    if test_time:
        print('*** Time tests config: {}'.format(
            ' | '.join('{}: {}'.format(*item) for item in c.as_dict().items())))
        ######################################
        # test merging time (sorted sequences)
        print('*** Merging times...')
        for f in funcs_s:
            try:
                stmt = 'for pair in lsts: {}(*pair)'.format(f)
                t  = timeit.Timer(stmt=stmt, setup=setup, globals=locals()).timeit(c.repeat)
                print(report.format(f'{f}:', t/c.repeat))
            except RecursionError as e:
                print(report.format('[Fail] -> {}'.format(e)))
        ########################################
        # test sorting time (unsorted sequences)
        print('*** Sorting times...')
        # merge_sort
        stmt = 'for l in ichain(lstr): list(merge_sort(l))'
        t  = timeit.Timer(stmt=stmt, setup='from __main__ import merge_sort', globals=locals()).timeit(c.repeat)
        print(report.format('merge_sort:', t/c.repeat))
        # merge_sort2 | with merge_sorted_g
        stmt = 'for l in ichain(lstr): list(merge_sort2(l, func=merge_sorted_g))'
        t  = timeit.Timer(stmt=stmt, setup='from __main__ import merge_sort2, merge_sorted_g', globals=locals()).timeit(c.repeat)
        print(report.format('merge_sort2 (*_g):', t/c.repeat))
        # merge_sort2 | with merge_sorted_c
        stmt = 'for l in ichain(lstr): list(merge_sort2(l, func=merge_sorted_c))'
        t  = timeit.Timer(stmt=stmt, setup='from __main__ import merge_sort2, merge_sorted_c', globals=locals()).timeit(c.repeat)
        print(report.format('merge_sort2 (*_c):', t/c.repeat))
        try:
            # merge_sort2 | with merge_sorted_i
            stmt = 'for l in ichain(lstr): list(merge_sort2(l, func=merge_sorted_i))'
            t  = timeit.Timer(stmt=stmt, setup='from __main__ import merge_sort2, merge_sorted_i', globals=locals()).timeit(c.repeat)
            print(report.format('merge_sort2 (*_i):', t/c.repeat))
        except RecursionError as e:
            print('[FAIL] merge_sort2 (*_i): -> ', e)
        try:
            # merge_sort3 | with merge_sorted_i
            stmt = 'for l in ichain(lstr): list(merge_sort3(l, func=merge_sorted_i))'
            t  = timeit.Timer(stmt=stmt, setup='from __main__ import merge_sort3, merge_sorted_i', globals=locals()).timeit(c.repeat)
            print(report.format('merge_sort3 (*_i):', t/c.repeat))
        except RecursionError as e:
            print('[FAIL] merge_sort3 (*_i): -> ', e)
            # builtin sorted
        stmt = 'for l in ichain(lstr): sorted(l)'
        t  = timeit.Timer(stmt=stmt, globals=locals()).timeit(c.repeat)
        print(report.format('(builtin) sorted:', t/c.repeat))

    
def get_parsed(test_config):
    c = test_config
    p = argparse.ArgumentParser()
    p.add_argument('-m', '--min', dest='min', type=int, default=c.min, help="(test) lists min value (%(default)s)")
    p.add_argument('-M', '--max', dest='max', type=int, default=c.max, help='(test) lists max value (%(default)s)')
    p.add_argument('-l', '--len', dest='len', type=int, default=c.len, help='(test) number of lists pairs (%(default)s)')
    p.add_argument('-r', '--repeat', dest='repeat', type=int, default=c.repeat, help='(test) timeit() repeat value (%(default)s)')
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
    c = Config()
    p = get_parsed(c)
    for k,v in c.as_dict().items():
        c[k] = getattr(p, k)
    if p.test_time or p.test_funcs:
        _test(c, inputs, test_time=p.test_time, test_funcs=p.test_funcs, debug=p.debug, stats=p.stats)
        if p.quit:
            sys.exit(0)
    # brief example
    for lsts in inputs:
        print('------\n[MS]  input: {0[0]} {0[1]} -> {1}'.format(
            lsts, merge_sorted(*lsts)))
        print('[MSG] input: {0[0]} {0[1]} -> {1}'.format(
            lsts, list(merge_sorted_g(*lsts))))





""" ###XXXLenta... lenta... bisogna trovare una soluzione per sto cazzo di RecursionError
crap0101@orange:~/test$ python3  merge-sort+Injecretor.py -tsqT -m-100 -M100 -l 100 -r 10
test Injecretor: OK
*** Test merging...
assert (merge) [short]: OK
assert (merge) [short]: OK
assert (merge-sort): OK
assert (group_sort*): OK
function sort_two:            0.000602977s
function group_sort:          0.000274483s
function group_sort2:         0.000559615s
***Some stats (merging):
list pairs:        100
lists min value:       -100
lists max value:         96
Longer list:           178 items
Shorter list:            0 items
average length:      59.25
Total items:         11850
*** Time tests config: min: -100 | max: 100 | len: 100 | repeat: 10
*** Merging times...
function merge_sorted:        0.00408618s
function merge_sorted_c:      0.0203727s
function merge_sorted_g:      0.0182151s
function merge_sorted_i:      2.95963e-05s
*** Sorting times...
function merge_sort:          0.377423s
function merge_sort2 (*_g):   0.37226s
function merge_sort2 (*_c):   0.404886s
function merge_sort2 (*_i):   0.386429s
function merge_sort3 (*_i):   0.142802s
function (builtin) sorted:    0.000948465s
_test runs in: 20.9905 seconds
"""    

"""
crap0101@orange:~/test$ python3  merge-sort+Injecretor.py -tsqT -m-300 -M300 -l 50 -r 10
test Injecretor: OK
*** Test merging...
assert (merge) [short]: OK
assert (merge) [short]: OK
assert (merge-sort): OK
assert (group_sort*): OK
function sort_two:            0.00146732s
function group_sort:          0.000660176s
function group_sort2:         0.00138216s
***Some stats (merging):
list pairs:         50
lists min value:       -293
lists max value:        283
Longer list:           509 items
Shorter list:            5 items
average length:     169.44
Total items:         16944
*** Time tests config: min: -300 | max: 300 | len: 50 | repeat: 10
*** Merging times...
function merge_sorted:        0.00572258s
function merge_sorted_c:      0.0285029s
function merge_sorted_g:      0.0248084s
function merge_sorted_i:      1.50123e-05s
*** Sorting times...
function merge_sort:          1.43732s
function merge_sort2 (*_g):   1.40806s
function merge_sort2 (*_c):   1.53833s
function merge_sort2 (*_i):   1.65459s
function merge_sort3 (*_i):   0.248425s
function (builtin) sorted:    0.00166128s
_test runs in: 67.0474 seconds
"""

"""
crap0101@orange:~/test$ python3  merge-sort+Injecretor.py -tsqT -m100 -M100 -l 100 -h
usage: merge-sort+Injecretor.py [-h] [-m MIN] [-M MAX] [-l LEN] [-r REPEAT]
                                [-t] [-T] [-q] [-d] [-s]

optional arguments:
  -h, --help            show this help message and exit
  -m MIN, --min MIN     (test) lists min value (-10000)
  -M MAX, --max MAX     (test) lists max value (10000)
  -l LEN, --len LEN     (test) number of lists pairs (1001)
  -r REPEAT, --repeat REPEAT
                        (test) timeit() repeat value (1000)
  -t, --test-time       test time
  -T, --test-functions  test functions
  -q, --quit            quit after tests
  -d, --debug           print debug info (tests only)
  -s, --stats           print some stat (tests only)
"""

"""
crap0101@orange:~/test$ python3 merge-sort+Injecretor.py 
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
------
[MS]  input: range(0, 1) range(1, 2) -> [0, 1]
[MSG] input: range(0, 1) range(1, 2) -> [0, 1]
"""
