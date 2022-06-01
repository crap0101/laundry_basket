#!/usr/bin/env python3
# >= 3.8.10

import argparse
import collections 
from collections.abc import Sequence, Callable, Iterable
import functools
import heapq
import itertools
import sys
import time


###################
# utility classes #
###################


class Config:
    def __new__ (cls, **k):
        inst = super().__new__(cls)
        inst.fields = ('min', 'max', 'len', 'flen', 'repeat')
        inst.defvalues = (-10000, 10000, 1001, 8000, 1000)
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

########################
# strumental functions #
########################

def timer (f):
    def inner (*a, **k):
        ts = time.time()
        ret = f(*a, **k)
        t = time.time() - ts
        print(f'{f.__name__} runs in: {t:.4f} seconds')
        return ret
    return inner

#####################
# utility functions #
#####################

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
    idx = 1
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

def takes_f (seq: Sequence, n: int, fillvalue=None) -> Iterable:
    """Yields chunk of `n` items a times from `seq`"""
    it = iter(seq)
    while True:
        p = list(itertools.islice(it, 0, n))
        if not p:
            return
        if len(p) < n:
            p.extend([fillvalue]*(n-len(p)))
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
                yield lst
                lst = []
                it.send(i)
                break
    if lst:
        yield lst

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

#XXX+TODO?: change sign+impl: f(seq, ofunc=group_sort|sort_two|other..., mfunc=merge_sorted_*)
def merge_sort (seq: Sequence, func: Callable = merge_sorted_g) -> Sequence:
    """Merge-sort."""
    #reduce = functools.reduce
    return list(functools.reduce(func, sort_two(seq), []))


def merge_sort2 (seq: Sequence, func: Callable = merge_sorted_g) -> Sequence:
    """Merge-sort... take advantage from partial ordered seqs."""
    #reduce = functools.reduce
    return list(functools.reduce(lambda a,b: list(func(a,b)), group_sort(seq), []))

def merge_sort3 (seq: Sequence, func: Callable = merge_sorted_i) -> Sequence:
    """merge sort...take advantage from partial ordered seqs"""
    d = collections.deque(group_sort(seq))
    if not d:
        return []
    while len(d) > 1:
        a = d.pop()
        b = d.pop()
        d.append(list(func(a, b)))#d.appendleft(func(a, b))
    assert len(d) == 1
    return d.pop()

def merge_sort4 (seq: Sequence, func: Callable = merge_sorted_i) -> Sequence:
    """merge sort...take advantage from partial ordered seqs"""
    s = []
    for a,b in takes_f(group_sort(seq), 2):
        s.append(a if b is None else tuple(func(a,b)))
    if not s:
        return []
    while len(s) > 1:
        ss = []
        for a,b in takes_f(s, 2):
            ss.append(a if b is None else tuple(func(a,b)))
        if ss:
            s = ss
    return s[0]




##########################################
# for comparison, others sorting methods #
##########################################

def bubble_sort (seq):
    s = list(seq)
    for i in range(len(s)):
        for j in range((len(s)-1)):
            if s[j] > s[j+1]:
                s[j], s[j+1] = s[j+1], s[j]
    return s


def heap_sort (seq):
    s = list(seq)
    heapq.heapify(s)
    return list(heapq.heappop(s) for _ in range(len(s)))
    

#########
# Tests #
#########

def _test_iter (seqs):
    for s in seqs:
        it = Injecretor(s)
        for i in it:
            pass
    print('*** Test Injecretor: OK')

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

def _test_msort (other_cmp=False):
    from random import randint as ri
    from random import shuffle
    fmt_others = ''
    lsts = [list(range(ri(-100,100),ri(100,200))) for _ in range(100)]
    for lst in lsts:
        shuffle(lst)
    for lst in lsts:
        s1 = list(merge_sort(lst, func=merge_sorted))
        s2 = list(merge_sort(lst, func=merge_sorted_g))
        s3 = list(merge_sort(lst, func=merge_sorted_c))
        s4 = list(merge_sort2(lst))
        s5 = list(merge_sort2(lst, func=merge_sorted_c))
        s6 = list(merge_sort3(lst, func=merge_sorted_i))
        s7 = list(merge_sort4(lst, func=merge_sorted_i))
        s8 = sorted(lst)
        assert s1 == s2, 'ERR (merge sort: merge_sorted <> merge_sorted_g): {} != {}'.format(s1, s2)
        assert s1 == s3, 'ERR (merge_sort: merge_sorted <> merge_sorted_c): {} != {}'.format(s1, s3)
        assert s1 == s4, 'ERR (merge_sort <> merge_sort2 (merge_sorted_g)): {} != {}'.format(s1, s4)
        assert s1 == s5, 'ERR (merge_sort <> merge_sort2 (merge_sorted_c)): {} != {}'.format(s1, s5)
        assert s1 == s6, 'ERR (merge_sort <> merge_sort3 (merge_sorted_i)): {} != {}'.format(s1, s6)
        assert s1 == s7, 'ERR (merge_sort <> merge_sort4 (merge_sorted_4)): {} != {}'.format(s1, s7)
        assert s1 == s8, 'ERR (merge_sort <> builtin sorted): {} != {}'.format(s1, s8)
        if other_cmp:
            fmt_others = '|others'
            s9 = bubble_sort(lst)
            s10 = heap_sort(lst)
            assert s1 == s9, 'ERR (merge_sort <> bubble_sort): {} != {}'.format(s1, s9)
            assert s1 == s10, 'ERR (merge_sort <> heap_sort): {} != {}'.format(s1, 10)
    print('assert (merge-sort{}): OK'.format(fmt_others))

def _test_sorting_vs_merging (sort_func, pair, merge_func=merge_sorted_i):
    lst, lst2 = pair
    totlst = lst + lst2
    # sort the list at once
    t0 = time.time()
    r1 = list(sort_func(totlst))
    t1 = time.time()
    print('sorting func: {} | merging func: {}'.format(sort_func.__name__, merge_func.__name__))
    print('sort at once:     {:.4f}'.format(t1-t0))
    # sort the lists, then merge
    t0 = time.time()
    p1 = sort_func(lst)
    p2 = sort_func(lst2)
    r2 = list(merge_func(p1, p2))
    t1 = time.time()
    print('sort, then merge: {:.4f}'.format(t1-t0))
    assert r1 == r2, '[FAIL] got different results! {} \n\n!=\n\n {}'.format(r1, r2)


@timer
def _test (config, *in_args, other_cmp=False, test_time=False, test_funcs=False, debug=False, stats=False):
    from copy import deepcopy
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
    report  = 'function {:30} {:.6f}s'
    # pair two by two, sorted lists
    if c.flen:
        # fixed length
        lsts = [[sorted(ri(c.min, c.max) for i in range(c.flen)),
                 sorted(ri(c.min, c.max) for i in range(c.flen))] for j in range(c.len)]
    else:
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
    test_cons_lst = deepcopy(lstr) 
    if debug:
        print('\n'.join(
            ' | '.join(f'len:{len(l):<5} min:{min(l,default=nan):<5} max:{max(l,default=nan):<5}'
                       for l in pair)
            for pair in lsts))
        for pair in lsts:
            for l in pair:
                assert list(l) == list(sorted(l))
                assert min(l) >= c.min and max(l) <= c.max, f'[FAIL] out of range: min: min(l) <? c.min | max(l) >? c.max'
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
            _test_msort(other_cmp)
        ###########################
        # test grouping and sorting
        for l in ichain(lstr[:5]):
            g1, g2 = group_sort(l), group_sort2(l)
            assert g1 == g2, "[FAIL] group_sort <> group_sort2"
            assert g1 == list(until_sorti(l)), "[FAIL] group_sort <> until_sorti"
        print('assert (group_sort*|until_sorti): OK')
        print('*** Grouping times:')
        stmt = 'for l in ichain(lstr[:10]): list(sort_two(l))'
        t  = timeit.Timer(stmt=stmt, setup='from __main__ import sort_two', globals=locals()).timeit(c.repeat)
        print(report.format('sort_two:', t/c.repeat))
        stmt = 'for l in ichain(lstr[:10]): list(group_sort(l))'
        t  = timeit.Timer(stmt=stmt, setup='from __main__ import group_sort', globals=locals()).timeit(c.repeat)
        print(report.format('group_sort:', t/c.repeat))
        stmt = 'for l in ichain(lstr[:10]): list(group_sort2(l))'
        t  = timeit.Timer(stmt=stmt, setup='from __main__ import group_sort2', globals=locals()).timeit(c.repeat)
        print(report.format('group_sort2:', t/c.repeat))
        stmt = 'for l in ichain(lstr[:10]): list(until_sorti(l))'
        t  = timeit.Timer(stmt=stmt, setup='from __main__ import until_sorti', globals=locals()).timeit(c.repeat)
        print(report.format('until_sorti:', t/c.repeat))

    if stats:
        __format = '{:<20} {}{}'
        print('***Some stats (merging):')
        print(__format.format('lists pairs', len(lsts), ''))
        for f, fname in [(min, 'min value'), (max, 'max value')]:
            r = f(itertools.chain(*itertools.chain.from_iterable(lsts)))
            print(__format.format('lists {}:'.format(fname), r, ''))
        llen = tuple(map(len,itertools.chain.from_iterable(lsts)))
        print(__format.format('Longer list:', max(llen), ' items'))
        print(__format.format('Shorter list:', min(llen), ' items'))
        print(__format.format('average length:', '{:.2f}'.format(sum(llen)/len(llen)), ''))
        print(__format.format('Total items:', sum(llen), ''))
    if test_time:
        print('*** Tests config: {}'.format(
            ' | '.join('{}: {}'.format(*item) for item in c.as_dict().items())))
        ######################################
        # test merging time (sorted sequences)
        print('*** Merging times...')
        for f in funcs_s:
            try:
                stmt = 'for pair in lsts: list({}(*pair))'.format(f)
                t  = timeit.Timer(stmt=stmt, setup=setup, globals=locals()).timeit(c.repeat)
                print(report.format(f'{f}:', t/c.repeat))
            except RecursionError as e:
                print(report.format('[Fail] -> {}'.format(e)))
        ###########################
        # test sort/merge diversion
        print('*** Sorting at once VS sorting then merging')
        _test_sorting_vs_merging(merge_sort4, lstr[0])
        _test_sorting_vs_merging(bubble_sort, lstr[0])
        ########################################
        # test sorting time (unsorted sequences)
        print('*** Sorting times...')
        # XXX+TODO: cmdline choose function to test
        """#
        # merge_sort
        stmt = 'for l in ichain(lstr): list(merge_sort(l))'
        t  = timeit.Timer(stmt=stmt, setup='from __main__ import merge_sort', globals=locals()).timeit(c.repeat)
        print(report.format('merge_sort (merge_sorted_g):', t/c.repeat))
        # merge_sort2 | with merge_sorted
        stmt = 'for l in ichain(lstr): list(merge_sort2(l, func=merge_sorted))'
        t  = timeit.Timer(stmt=stmt, setup='from __main__ import merge_sort2, merge_sorted', globals=locals()).timeit(c.repeat)
        print(report.format('merge_sort2 (merge_sorted):', t/c.repeat))
        # merge_sort2 | with merge_sorted_g
        stmt = 'for l in ichain(lstr): list(merge_sort2(l, func=merge_sorted_g))'
        t  = timeit.Timer(stmt=stmt, setup='from __main__ import merge_sort2, merge_sorted_g', globals=locals()).timeit(c.repeat)
        print(report.format('merge_sort2 (merge_sorted_g):', t/c.repeat))
        # merge_sort2 | with merge_sorted_c
        stmt = 'for l in ichain(lstr): list(merge_sort2(l, func=merge_sorted_c))'
        t  = timeit.Timer(stmt=stmt, setup='from __main__ import merge_sort2, merge_sorted_c', globals=locals()).timeit(c.repeat)
        print(report.format('merge_sort2 (merge_sorted_c):', t/c.repeat))
        try:
            # merge_sort2 | with merge_sorted_i
            stmt = 'for l in ichain(lstr): list(merge_sort2(l, func=merge_sorted_i))'
            t  = timeit.Timer(stmt=stmt, setup='from __main__ import merge_sort2, merge_sorted_i', globals=locals()).timeit(c.repeat)
            print(report.format('merge_sort2 (merge_sorted_i):', t/c.repeat))
        except RecursionError as e:
            print('[FAIL] merge_sort2 (merge_sorted_i): -> ', e)
        try:
            # merge_sort3 | with merge_sorted_i
            stmt = 'for l in ichain(lstr): list(merge_sort3(l, func=merge_sorted_i))'
            t  = timeit.Timer(stmt=stmt, setup='from __main__ import merge_sort3, merge_sorted_i', globals=locals()).timeit(c.repeat)
            print(report.format('merge_sort3 (merge_sorted_i):', t/c.repeat))
        except RecursionError as e:
            print('[FAIL] merge_sort3 (merge_sorted_i): -> ', e)
        #"""
        try:
            # merge_sort4 | with merge_sorted_i
            stmt = 'for l in ichain(lstr): list(merge_sort4(l, func=merge_sorted_i))'
            t  = timeit.Timer(stmt=stmt, setup='from __main__ import merge_sort4, merge_sorted_i', globals=locals()).timeit(c.repeat)
            print(report.format('merge_sort4 (merge_sorted_i):', t/c.repeat))
        except RecursionError as e:
            print('[FAIL] merge_sort4 (merge_sorted_i): -> ', e)
        try:
            # merge_sort4 | with merge_sorted
            stmt = 'for l in ichain(lstr): list(merge_sort4(l, func=merge_sorted))'
            t  = timeit.Timer(stmt=stmt, setup='from __main__ import merge_sort4, merge_sorted', globals=locals()).timeit(c.repeat)
            print(report.format('merge_sort4 (merge_sorted):', t/c.repeat))
        except RecursionError as e:
            print('[FAIL] merge_sort4 (merge_sorted): -> ', e)
            # builtin sorted
        stmt = 'for l in ichain(lstr): list(sorted(l))'
        t  = timeit.Timer(stmt=stmt, globals=locals()).timeit(c.repeat)
        print(report.format('(builtin) sorted:', t/c.repeat))
        if other_cmp:
            """#
            # bubble_sort
            stmt = 'for l in ichain(lstr): list(bubble_sort(l))'
            t  = timeit.Timer(stmt=stmt, setup='from __main__ import bubble_sort', globals=locals()).timeit(c.repeat)
            print(report.format('bubble_sort:', t/c.repeat))
            #"""
            # heap_sort
            stmt = 'for l in ichain(lstr): list(heap_sort(l))'
            t  = timeit.Timer(stmt=stmt, setup='from __main__ import heap_sort', globals=locals()).timeit(c.repeat)
            print(report.format('heap_sort:', t/c.repeat))
        #######################
        # final check, who say!
        for (a1, b1), (a2,b2) in zip(lstr, test_cons_lst):
            try:
                assert a1 == a2 and b1 == b2, "[FAIL]: input data changed during execution!!!"
            except AssertionError:
                break
        else:
            print('*** Test data consistency: OK')


def check_parser (p, parser):
    if p.min > p.max:
        parser.error('constrain violation: min > max')
    if p.len < 1:
        parser.error('constrain violation: len < 1')
    if p.repeat < 1:
        parser.error('constrain violation: repeat < 1')

def get_parsed(test_config):
    c = test_config
    p = argparse.ArgumentParser()
    p.add_argument('-m', '--min', dest='min', type=int, default=c.min,
                   metavar='N', help="(test) lists min value (%(default)s)")
    p.add_argument('-M', '--max', dest='max', type=int, default=c.max,
                   metavar='N', help='(test) lists max value (%(default)s)')
    p.add_argument('-l', '--len', dest='len', type=int, default=c.len, help='(test) number of lists pairs (%(default)s)')
    p.add_argument('-f', '--fixed-len', dest='flen', type=int, default=c.flen,
                   metavar='N', help='(test) generate lists with %(metavar)s items (default: %(default)s)')
    p.add_argument('-r', '--repeat', dest='repeat', type=int, default=c.repeat,
                   metavar='N', help='(test) timeit() repeat value (default: %(default)s)')
    p.add_argument('-t', '--test-time', dest='test_time', action='store_true', help='test time')
    p.add_argument('-T', '--test-functions', dest='test_funcs', action='store_true', help='test functions')
    p.add_argument('-C', '--compare-with', dest='other_cmp', action='store_true', help='(test) compare with others sorting functions')
    p.add_argument('-q', '--quit', dest='quit', action='store_true', help='quit after tests')
    p.add_argument('-d', '--debug', dest='debug', action='store_true', help='print debug info (tests only)')
    p.add_argument('-s', '--stats', dest='stats', action='store_true', help='print some stat (tests only)')    
    return p, p.parse_args()


if __name__ == '__main__':
    inputs = [([],[]), ([], range(5)), (range(9),[]),
        (range(10), range(5,15)),
        (range(6,12), range(5)),
        (range(10), range(2,6)),
        (range(2,6), range(10)),
        (range(1), range(1,2)),
    ]
    c = Config()
    parser, p = get_parsed(c)
    check_parser(p, parser)
    for k,v in c.as_dict().items():
        c[k] = getattr(p, k)
    if p.test_time or p.test_funcs:
        _test(c, inputs, other_cmp=p.other_cmp, test_time=p.test_time, test_funcs=p.test_funcs, debug=p.debug, stats=p.stats)
        if p.quit:
            sys.exit(0)
    # brief example
    for lsts in inputs:
        print('------\n[MS]  input: {0[0]} {0[1]} -> {1}'.format(
            lsts, merge_sorted(*lsts)))
        print('[MSG] input: {0[0]} {0[1]} -> {1}'.format(
            lsts, list(merge_sorted_g(*lsts))))



""" #XXX+TODO: mmm.. qualquadra non cosa, i test merge+sort separati con sorted danno risultati che dovrebbero essere opposti... o no?
crap0101@orange:~/test$ python3   merge-sort+Injecretor.py -tsqTC  -l 1 -f 10000 -r 1  # manual source edit, cut some funcs
*** Test Injecretor: OK
*** Test merging...
assert (merge) [short]: OK
assert (merge) [short]: OK
assert (merge-sort|others): OK
assert (group_sort*|until_sorti): OK
*** Grouping times:
function sort_two:                      0.011508s
function group_sort:                    0.006127s
function group_sort2:                   0.011352s
function until_sorti:                   0.026530s
***Some stats (merging):
lists pairs          1
lists min value:     -10000
lists max value:     10000
Longer list:         10000 items
Shorter list:        10000 items
average length:      10000.00
Total items:         20000
*** Tests config: min: -10000 | max: 10000 | len: 1 | flen: 10000 | repeat: 1
*** Merging times...
function merge_sorted:                  0.009053s
function merge_sorted_c:                0.036091s
function merge_sorted_g:                0.032321s
function merge_sorted_i:                0.031789s
*** Sorting at once VS sorting then merging
sorting func: merge_sort4 | merging func: merge_sorted_i
sort at once: 0.5320
sort, then merge: 0.5276
sorting func: bubble_sort | merging func: merge_sorted_i
sort at once: 99.6497
sort, then merge: 42.4056
*** Sorting times...
function merge_sort4 (merge_sorted_i):  0.492202s
function merge_sort4 (merge_sorted):    0.123019s
function (builtin) sorted:              0.004057s
function heap_sort:                     0.014773s
*** Test data consistency: OK
_test runs in: 149.5972 seconds
"""

"""
crap0101@orange:~/test$ python3  merge-sort+Injecretor.py -tsqTC -m100 -M600 -l 100 -r 5 
*** Test Injecretor: OK
*** Test merging...
assert (merge) [short]: OK
assert (merge) [short]: OK
assert (merge-sort|others): OK
assert (group_sort*|until_sorti): OK
*** Grouping times:
function sort_two:                      0.001349s
function group_sort:                    0.000606s
function group_sort2:                   0.001294s
function until_sorti:                   0.003562s
***Some stats (merging):
lists pairs          100
lists min value:     0
lists max value:     599
Longer list:         468 items
Shorter list:        3 items
average length:      167.33
Total items:         33466
*** Tests config: min: 100 | max: 600 | len: 100 | repeat: 5
*** Merging times...
function merge_sorted:                  0.012176s
function merge_sorted_c:                0.056200s
function merge_sorted_g:                0.049226s
function merge_sorted_i:                0.049015s
*** Sorting times...
function merge_sort (merge_sorted_g):   2.551426s
function merge_sort2 (merge_sorted):    0.623720s
function merge_sort2 (merge_sorted_g):  2.588979s
function merge_sort2 (merge_sorted_c):  2.852323s
function merge_sort2 (merge_sorted_i):  2.492043s
function merge_sort3 (merge_sorted_i):  2.554920s
function merge_sort4 (merge_sorted_i):  0.513805s
function merge_sort4 (merge_sorted):    0.121229s
function (builtin) sorted:              0.003178s
function bubble_sort:                   1.619951s
function heap_sort:                     0.015377s
Test data consistency: OK
_test runs in: 86.2501 seconds
"""

"""
crap0101@orange:~/test$ python3 merge-sort+Injecretor.py -h
usage: merge-sort+Injecretor.py [-h] [-m N] [-M N] [-l LEN] [-f N] [-r N] [-t]
                                [-T] [-C] [-q] [-d] [-s]

optional arguments:
  -h, --help            show this help message and exit
  -m N, --min N         (test) lists min value (-10000)
  -M N, --max N         (test) lists max value (10000)
  -l LEN, --len LEN     (test) number of lists pairs (1001)
  -f N, --fixed-len N   (test) generate lists with N items (default: 8000)
  -r N, --repeat N      (test) timeit() repeat value (default: 1000)
  -t, --test-time       test time
  -T, --test-functions  test functions
  -C, --compare-with    (test) compare with others sorting functions
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


######## other runs... mainly from previous revisions

""" ###XXX+TODO: Lenta... lenta...
crap0101@orange:~/test$ python3  merge-sort+Injecretor.py -tsqTC -m-300 -M500 -l 100 -r 10 
test Injecretor: OK
*** Test merging...
assert (merge) [short]: OK
assert (merge) [short]: OK
assert (merge-sort): OK
assert (group_sort*|until_sorti): OK
function sort_two:            0.001749s
function group_sort:          0.000750s
function group_sort2:         0.001701s
function until_sorti:         0.004433s
***Some stats (merging):
list pairs:        100
lists min value:       -297
lists max value:        490
Longer list:           728 items
Shorter list:            3 items
average length:     210.49
Total items:         42098
*** Time tests config: min: -300 | max: 500 | len: 100 | repeat: 10
*** Merging times...
function merge_sorted:        0.015531s
function merge_sorted_c:      0.070140s
function merge_sorted_g:      0.060672s
function merge_sorted_i:      0.060177s
*** Sorting times...
function merge_sort:          4.156328s
function merge_sort2 (*_g):   4.176925s
function merge_sort2 (*_c):   4.567855s
function merge_sort2 (*_i):   4.023452s
function merge_sort3 (*_i):   4.114324s
function merge_sort4 (*_i):   0.700929s
function (builtin) sorted:    0.004408s
function bubble_sort:         2.599283s
Test data consistency: OK
_test runs in: 250.8556 seconds
"""    

""" ### Seems not so stable ^L^
crap0101@orange:~/test$ python3  merge-sort+Injecretor.py -tsqTC -r 1 -l 1
test Injecretor: OK
*** Test merging...
assert (merge) [short]: OK
assert (merge) [short]: OK
assert (merge-sort): OK
assert (group_sort*|until_sorti): OK
function sort_two:            0.000949s
function group_sort:          0.000417s
function group_sort2:         0.000919s
function until_sorti:         0.002279s
***Some stats (merging):
list pairs:          1
lists min value:          0
lists max value:       3333
Longer list:           902 items
Shorter list:          902 items
average length:     902.00
Total items:          1804
*** Time tests config: min: -10000 | max: 10000 | len: 1 | repeat: 1
*** Merging times...
function merge_sorted:        0.000681s
function merge_sorted_c:      0.003009s
function merge_sorted_g:      0.002676s
function merge_sorted_i:      0.002621s
*** Sorting times...
function merge_sort (*_g):    0.483354s
function merge_sort2 (merge_sorted): 0.124735s
function merge_sort2 (*_g):   0.491245s
function merge_sort2 (*_c):   0.530668s
function merge_sort2 (*_i):   0.466901s
function merge_sort3 (*_i):   0.490612s
function merge_sort4 (*_i):   0.034804s
function (builtin) sorted:    0.000229s
function bubble_sort:         0.322256s
Test data consistency: OK
_test runs in: 8.3609 seconds
crap0101@orange:~/test$ python3  merge-sort+Injecretor.py -tsqTC -r 1 -l 1
test Injecretor: OK
*** Test merging...
assert (merge) [short]: OK
assert (merge) [short]: OK
assert (merge-sort): OK
assert (group_sort*|until_sorti): OK
function sort_two:                      0.015538s
function group_sort:                    0.009027s
function group_sort2:                   0.015749s
function until_sorti:                   0.036427s
***Some stats (merging):
list pairs:          1
lists min value:      -8871
lists max value:       4769
Longer list:         13641 items
Shorter list:        13641 items
average length:   13641.00
Total items:         27282
*** Time tests config: min: -10000 | max: 10000 | len: 1 | repeat: 1
*** Merging times...
function merge_sorted:                  0.010913s
function merge_sorted_c:                0.046710s
function merge_sorted_g:                0.042386s
function merge_sorted_i:                0.041012s
*** Sorting times...
function merge_sort (merge_sorted_g):   105.623984s
function merge_sort2 (merge_sorted):    27.128372s
function merge_sort2 (merge_sorted_g):  105.725386s
function merge_sort2 (merge_sorted_c):  119.193799s
function merge_sort2 (merge_sorted_i):  101.951429s
function merge_sort3 (merge_sorted_i):  103.075798s
function merge_sort4 (merge_sorted_i):  0.668725s
function merge_sort4 (merge_sorted):    0.178412s
function (builtin) sorted:              0.006054s
function bubble_sort:                   78.496800s
Test data consistency: OK
_test runs in: 647.8974 seconds
"""

