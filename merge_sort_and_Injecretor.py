#!/usr/bin/env python3
# >= 3.8.10

import argparse
import bisect
import collections
from collections import deque
import functools
import heapq
import itertools
import sys
import random
import time
from typing import Callable, Collection, Iterable, Sequence
from typing import Any, Generic, TypeVar


####################################
# utility classes and other things #
####################################

T = TypeVar('T')
S = TypeVar('S')
class Pair(Generic[T,S]):
    pass
class IntSeq(Collection[int]):
    pass

# for iflatten:
IGNORED_TYPES = ()
NESTED_TYPES = (Collection,Sequence,Iterable,)
REC_TYPES = (str,bytes,)
# ^

MERGE_FUNCS_NAMES = 'merge_sorted merge_sorted_b merge_sorted_c merge_sorted_g merge_sorted_i'.split()
MSORT_FUNCS_NAMES = 'merge_sort merge_sort2 merge_sort3 merge_sort4 merge_sort5'.split()
OTHER_SORT_FUNC_NAMES = '_merge_sort5 heap_sort heap_sorti bubble_sort'.split()
GROUPING_FUNC_NAMES = 'group_sort group_sorti group_sort2 until_sorti'.split()

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
    """To be used as decorator to track time."""
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

# from https://github.com/crap0101/laundry_basket/blob/master/deepflatten.py
def iflatten (seq, ignore=IGNORED_TYPES):
    """deep-flat using list. Works with infinite sequences."""
    d = deque((iter(seq),))
    while d:
        x = d[0]
        for item in x:
            skip_ignored = isinstance(item, ignore)
            if isinstance(item, NESTED_TYPES):
                if isinstance(item, REC_TYPES):
                    if skip_ignored:
                        yield item
                    else:
                        for i in item:
                            yield i
                elif skip_ignored:
                    yield item
                else:
                    d.appendleft(iter(item))
                    break
            else:
                yield item
        else:
            d.popleft()

####################
##### GROUPING #####
####################

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

def group_sorti (seq: Sequence) -> Iterable:
    """Yields items from `seq` grouped while sorted."""
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
            yield lst
            a = i
            lst = [a]
    if lst:
        yield lst

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

def reduce(func: Callable, seq: Sequence, init: Any = None) -> Any:
    """Simple reduce function. use `init` as extra initial value."""
    it = iter(seq)
    if init is None:
        val = next(it)
    else:
        val = init
    for i in it:
        val = func(val, i)
    return val

def sort_two (seq: Sequence) -> Sequence:
    """Return sorted seqs of items, two by two.
    Items must support the `>` operator."""
    pairs = []
    for lst in takes(seq, 2):
        if len(lst) == 1:
            pairs.append(tuple(lst))
        else:
            a, b = lst
            pairs.append((b,a) if a > b else (a, b))
    return pairs

def isort_two (seq: Sequence) -> Iterable:
    """Return sorted seqs of items, two by two.
    Items must support the `>` operator."""
    for take in takes(seq, 2):
        if len(take) == 1:
            yield tuple(take)
        else:
            a, b = take
            yield (b,a) if a > b else (a, b)


def takes (seq: Sequence, n: int) -> Iterable:
    """Yields chunk of `n` items a times from `seq`"""
    it = iter(seq)
    while True:
        p = tuple(itertools.islice(it, 0, n))
        if not p:
            return
        yield p

def takes_f (seq: Sequence, n: int, fillvalue: Any = None) -> Iterable:
    """Yields chunk of *exactly* `n` items a times from `seq`.
    Use `fillvalue` as replacement for missing values."""
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

def zip_2 (s1: Sequence, s2: Sequence, fillvalue: Any = None) -> Iterable:
    """Yields pairs of items from `s1` and `s2` stopping at the
    end of the shorter sequence, with missing value replaced by `fillvalue`."""
    _quit = 0
    QUIT = 2
    is1 = iter(s1)
    is2 = iter(s2)
    while True:
        _quit = 0
        ret = []
        try:
            v1 = next(is1)
            ret.append(v1)
        except StopIteration:
            ret.append(fillvalue)
            _quit += 1
        try:
            v2 = next(is2)
            ret.append(v2)
        except StopIteration:
            ret.append(fillvalue)
            _quit += 1
        if _quit == QUIT:
            return
        yield tuple(ret)

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

def merge_sorted_b (s1: Sequence, s2: Sequence) -> Iterable:
    """Merge two ordered sequences returning a third. Use bisect."""
    m = list(s1)
    low = 0
    for item in s2:
        idx = bisect.bisect_left(m, item, low)
        bisect.insort_left(m, item, idx)
        low = idx
    return m

def merge_sorted_c (s1: Sequence, s2: Sequence) -> Iterable:
    """Merge two ordered sequences returning a third. Better."""
    merged = collections.deque()
    g1 = Injecretor(s1,name='s1')
    g2 = Injecretor(s2,name='s2')
    while True:
        try:
            i = next(g1)
        except StopIteration:
            i = None
        try:
            j = next(g2)
        except StopIteration:
            j = None
        try:
            if i <= j:
                merged.append(i)
                g2.send(j)
            else:
                merged.append(j)
                g1.send(i)
        except TypeError as e:
            if i is None and j is None:
                break
            elif i is None:
                g2.send(j)
                merged.extend(g2)
                break
            elif j is None:
                g1.send(i)
                merged.extend(g1)
                break
            else:
                raise e
    return merged


def merge_sorted_g (s1: Sequence, s2: Sequence) -> Sequence:
    """Merge two ordered sequences returning a third."""
    g1 = Injecretor(s1,name='s1')
    g2 = Injecretor(s2,name='s2')
    merged = []
    for i, j in itertools.zip_longest(g1, g2, fillvalue=None):
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
    merged.extend(g1)
    merged.extend(g2)
    return merged

def merge_sorted_i (s1: Sequence, s2: Sequence) -> Iterable:
    """Merge two ordered sequences, returns an iterator over the resulting seq."""
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
    """merge sort...take advantage from partial ordered seqs."""
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
    """merge sort...take advantage from partial ordered seqs."""
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

def _merge_sort5 (seq: Sequence, func : Callable = None) -> Sequence: # NOTE: func parameter not used
    sorted_pairs = group_sorti(seq)
    while True:
        s = []
        for p1, p2 in takes_f(sorted_pairs, 2, ()):
            m = p1 #list(p1)
            low = 0
            for p in p2:
                idx = bisect.bisect_left(m, p, low)
                bisect.insort_left(m, p, idx)
                low = idx
            s.append(m)
        sorted_pairs = s
        if not s:
            sorted_pairs = [s]
            break
        elif len(sorted_pairs) == 1:
            break
    return sorted_pairs[0]

def merge_sort5 (seq: Sequence, func : Callable = merge_sorted_b) -> Sequence:
    return list(functools.reduce(lambda a,b: list(func(a,b)), group_sorti(seq), []))


##########################################
# for comparison, others sorting methods #
##########################################

def bubble_sort (seq: IntSeq, func: Any = None) -> Sequence:
    """Bubble sort. `func` parameter ignored
    (here just for compatibility with merge_sort* funcs)."""
    s = list(seq)
    for i in range(len(s)):
        for j in range((len(s)-1)):
            if s[j] > s[j+1]:
                s[j], s[j+1] = s[j+1], s[j]
    return s

def heap_sort (seq: Sequence, func: Any = None) -> Sequence:
    """Heap sort. `func` parameter ignored
    (here just for compatibility with merge_sort* funcs)."""
    s = list(seq)
    heapq.heapify(s)
    return list(heapq.heappop(s) for _ in range(len(s)))

def heap_sorti (seq: Sequence, func: Any = None) -> Iterable:
    """Heap sort. `func` parameter ignored
    (here just for compatibility with merge_sort* funcs)."""
    s = list(seq)
    heapq.heapify(s)
    while s:
        yield heapq.heappop(s)
    

#########
# Tests #
#########

def _test_iter (seqs: Collection[Sequence]):
    for s in seqs:
        it = Injecretor(s)
        for i in it:
            pass
    print('Injecretor: OK')

def _test_merged (fnames: Collection[str], lst: Collection[Pair[IntSeq, IntSeq]]):
    funcs = list(itertools.combinations((globals()[name] for name in fnames), 2))
    for pair in lst:
        for f1, f2 in funcs:
            r1 = list(f1(*pair))
            r2 = list(f2(*pair))
            assert r1 == r2, f'[FAIL]: {f1.__name__} <> {f2.__name}'
    print('assert (merge): OK')


def _test_msort (msort_names, merge_names, other_names, compare_others: bool):
    ri = random.randint
    shuffle = random.shuffle
    lsts = [list(range(ri(-100,100),ri(100,200))) for _ in range(100)]
    for lst in lsts:
        shuffle(lst)
    msort_f = list(globals()[name] for name in msort_names)
    merge_f = list(globals()[name] for name in merge_names)
    other_f = list(globals()[name] for name in other_names)
    fpairs = list(itertools.product(msort_f, merge_f))
    for lst in lsts:
        f1, f2 = fpairs[0]
        r1 = list(f1(lst, f2))
        for ff1, ff2 in fpairs[1:]:
            r2 = list(ff1(lst, ff2))
            assert r1 == r2, f'[FAIL] {f1.__name__}({f2.__name__}) <> {ff1.__name__}({ff2.__name__}) {r1} \n\n {r2}'
        # compare with builtin sorted anyway
        rs = sorted(lst)
        assert r1 == rs, f'[FAIL] {f1.__name__}({f2.__name__}) <> builtin sorted()'
        if compare_others:
            for f in other_f:
                ro = list(f(lst))
                assert r1 == ro, f'[FAIL] {f1.__name__}({f2.__name__}) <> {f.__name__}'
    print('assert (merge-sort): OK')

def _test_sorting_vs_merging (sort_func, pair: Pair[Sequence,Sequence], merge_func=merge_sorted_i):
    pair = map(list, pair)
    lst, lst2 = pair
    totlst = lst + lst2
    _fail = 0
    # sort the list at once
    print('sorting func: {} | merging func: {}'.format(sort_func.__name__, merge_func.__name__))
    try:
        print('{:20}'.format('sort at once:'), end='')
        t0 = time.time()
        r1 = list(sort_func(totlst, merge_func))
        t1 = time.time()
        print('{:.4f}'.format(t1-t0))
    except RecursionError as e:
        print('[Fail] {} | {} -> {}'.format(sort_func.__name__, merge_func.__name__, e))
        _fail = 1
    # sort the lists, then merge
    try:
        print('{:20}'.format('sort, then merge:'), end='')
        t0 = time.time()
        p1 = sort_func(lst)
        p2 = sort_func(lst2)
        r2 = list(merge_func(p1, p2))
        t1 = time.time()
        print('{:.4f}'.format(t1-t0))
    except RecursionError as e:
        print('[Fail] {} | {} -> {}'.format(sort_func.__name__, merge_func.__name__, e))
        _fail = 1
    if not _fail:
        assert r1 == r2, '[FAIL] got different results! {} \n\n!=\n\n {}'.format(r1, r2)


@timer
def _test (config, parsed_cmdline):
    from copy import deepcopy
    from math import nan
    import timeit
    ichain = itertools.chain.from_iterable
    ri = random.randint
    shuffle = random.shuffle
    c = config
    p = parsed_cmdline
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
    if p.debug:
        print('\n'.join(
            ' | '.join(f'len:{len(l):<5} min:{min(l,default=nan):<5} max:{max(l,default=nan):<5}'
                       for l in pair)
            for pair in lsts))
        #
        for pair in lsts:
            for l in pair:
                assert list(l) == list(sorted(l))
                assert min(l) >= c.min and max(l) <= c.max, f'[FAIL] out of range: min: min(l) <? c.min | max(l) >? c.max'
        print('assert (sorted input): OK')
    if p.test_funcs:
        ################
        # test iteration
        print('*** Test iterators...')
        _test_iter(ichain(lstr))
        ###############
        # test merging
        print('*** Test merging...')
        _test_merged(p.merge_funcs, lsts[:2])
        _test_msort(p.msort_funcs, p.merge_funcs, p.other_sort_funcs, p.other_cmp)
        ###########################
        # test grouping and sorting
        print('*** Test grouping...')
        for l in ichain(lstr[:5]):
            gf = list(itertools.combinations([globals()[name] for name in p.group_funcs], 2))
            for f1, f2 in gf:
                r1, r2 = list(f1(l)), list(f2(l))
                assert r1 == r2, f"[FAIL] {f1.__name__} <> {f2.__name__}"
        print('assert ({}): OK'.format(', '.join(p.group_funcs)))
        #####################
        # Miscellaneous tests
        print('*** Tests misc...')
        # sort_two would belongs to the sorting funcs, set aside because
        # it works a little differently (and slower!)
        for l in ichain(lstr[:5]):
            assert sort_two(l) == list(isort_two(l)), '[FAIL]: (sort) sort_two <> isort_two'
            for tup1, tup2 in zip(sort_two(l), isort_two(l)):
                assert tup1 == tup2,  '[FAIL]: (tup) sort_two <> isort_two'
                if len(tup1) == 2:
                    assert tup1[0] <= tup1[1], f'[FAIL]: sort_two: {tup[0]} > {tup[1]}'
        print('sort_two|isort_two: OK')
    if p.stats:
        __format = '{:<20} {}{}'
        print('*** Some stats (merging):')
        print(__format.format('lists pairs', len(lsts), ''))
        for f, fname in [(min, 'min value'), (max, 'max value')]:
            r = f(itertools.chain(*itertools.chain.from_iterable(lsts)))
            print(__format.format('lists {}:'.format(fname), r, ''))
        llen = tuple(map(len,itertools.chain.from_iterable(lsts)))
        print(__format.format('Longer list:', max(llen), ' items'))
        print(__format.format('Shorter list:', min(llen), ' items'))
        print(__format.format('average length:', '{:.2f}'.format(sum(llen)/len(llen)), ''))
        print(__format.format('Total items:', sum(llen), ''))
        print(__format.format('Unique elements:', len(set(iflatten(lsts))), ''))
    if p.test_time:
        print('*** Test times...')
        print('** config: {}'.format(
            ' | '.join('{}={}'.format(*item) for item in c.as_dict().items())))
        ####################
        # test grouping time
        print('** Grouping times:')
        for f in p.group_funcs:
            gf_setup = 'from __main__ import {}'.format(f)
            gf_stmt = 'for l in ichain(lstr[:10]): list({}(l))'.format(f)
            t  = timeit.Timer(stmt=gf_stmt, setup=gf_setup, globals=locals()).timeit(c.repeat)
            print(report.format(f'{f}:', t/c.repeat))
        print('** sort_two times:')
        for f in ('sort_two', 'isort_two'):
            sf_setup = 'from __main__ import {}'.format(f)
            sf_stmt = 'for l in ichain(lstr[:10]): list({}(l))'.format(f)
            t  = timeit.Timer(stmt=sf_stmt, setup=sf_setup, globals=locals()).timeit(c.repeat)
            print(report.format(f'{f}:', t/c.repeat))

        ######################################
        # test merging time (sorted sequences)
        print('** Merging times...')
        for f in p.merge_funcs:
            try:
                mf_setup = 'from __main__ import {}'.format(f)
                mf_stmt = 'for pair in lsts: list({}(*pair))'.format(f)
                t  = timeit.Timer(stmt=mf_stmt, setup=mf_setup, globals=locals()).timeit(c.repeat)
                print(report.format(f'{f}:', t/c.repeat))
            except RecursionError as e:
                print(report.format('[Fail] -> {}'.format(e)))
        ###########################
        # test sort/merge diversion
        print('** Sorting at once VS sorting then merging')
        for sort_func, merge_func in itertools.product(ichain([p.msort_funcs, p.other_sort_funcs]), p.merge_funcs):
            _test_sorting_vs_merging(globals()[sort_func], lstr[0], merge_func=globals()[merge_func])
        ########################################
        # test sorting time (unsorted sequences)
        print('** Sorting times...')
        for sort_func, merge_func in itertools.product(p.msort_funcs, p.merge_funcs):
            try:
                m_setup = f'from __main__ import {sort_func}, {merge_func}'
                m_stmt = 'for l in ichain(lstr): list({}(l, func={}))'.format(sort_func, merge_func)
                t  = timeit.Timer(stmt=m_stmt, setup=m_setup, globals=locals()).timeit(c.repeat)
                print(report.format(f'{sort_func} ({merge_func}):', t/c.repeat))
            except RecursionError as e:
                print(f'[FAIL] {sort_func} ({merge_func}): -> ', e)
        # builtin sorted
        stmt = 'for l in ichain(lstr): list(sorted(l))'
        t  = timeit.Timer(stmt=stmt, globals=locals()).timeit(c.repeat)
        print(report.format('(builtin) sorted:', t/c.repeat))
        #
        if p.other_cmp:
            for f in p.other_sort_funcs:
                o_setup = f'from __main__ import {f}'
                o_stmt = f'for l in ichain(lstr): list({f}(l))'
                t  = timeit.Timer(stmt=o_stmt, setup=o_setup, globals=locals()).timeit(c.repeat)
                print(report.format(f'{f}:', t/c.repeat))
        #######################
        # final check, who say! ^-^
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
    p.add_argument('-G', '--grouping-funcs', dest='group_funcs', choices=GROUPING_FUNC_NAMES, nargs='+', default=GROUPING_FUNC_NAMES,
                   metavar='NAME', help='grouping functions to test, choice from: %(choices)s. Default: all.')
    p.add_argument('-F', '--funcs', dest='msort_funcs', choices=MSORT_FUNCS_NAMES, nargs='+', default=MSORT_FUNCS_NAMES,
                   metavar='NAME', help='merge-sort functions to test, choice from: %(choices)s. Default: all.')
    p.add_argument('-u', '--merge-funcs', dest='merge_funcs', choices=MERGE_FUNCS_NAMES, nargs='+', default=MERGE_FUNCS_NAMES,
                   metavar='NAME', help='merging functions to test, choice from: %(choices)s. Default: all.')
    p.add_argument('-C', '--compare-with', dest='other_cmp', action='store_true', help='(test) compare with others sorting functions')
    p.add_argument('-O', '--other-funcs', dest='other_sort_funcs', choices=OTHER_SORT_FUNC_NAMES, nargs='+', default=OTHER_SORT_FUNC_NAMES,
                   metavar='NAME', help='other sort functions to test (when using the -C option), choice from: %(choices)s. Default: all.')
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
        _test(c, p)
        if p.quit:
            sys.exit(0)
    # brief example
    for lsts in inputs:
        print('------\n[MS]  input: {0[0]} {0[1]} -> {1}'.format(
            lsts, merge_sorted(*lsts)))
        print('[MSG] input: {0[0]} {0[1]} -> {1}'.format(
            lsts, list(merge_sorted_g(*lsts))))



"""
crap0101@orange:~/test$ python3 merge_sort_and_Injecretor.py -tsqTC -l 10 -m-1000 -M3000 -f 1001 -r 1 -F merge_sort merge_sort4 merge_sort5 -u merge_sorted_c merge_sorted_i merge_sorted_b 
*** Test iterators...
Injecretor: OK
*** Test merging...
assert (merge): OK
assert (merge-sort): OK
*** Test grouping...
assert (group_sort, group_sorti, group_sort2, until_sorti): OK
*** Tests misc...
sort_two|isort_two: OK
*** Some stats (merging):
lists pairs          10
lists min value:     -1000
lists max value:     3000
Longer list:         1001 items
Shorter list:        1001 items
average length:      1001.00
Total items:         20020
Unique elements:     3976
*** Test times...
** config: min=-1000 | max=3000 | len=10 | flen=1001 | repeat=1
** Grouping times:
function group_sort:                    0.004641s
function group_sorti:                   0.004352s
function group_sort2:                   0.009736s
function until_sorti:                   0.025343s
** sort_two times:
function sort_two:                      0.009982s
function isort_two:                     0.009538s
** Merging times...
function merge_sorted_c:                0.032963s
function merge_sorted_i:                0.028907s
function merge_sorted_b:                0.016299s
** Sorting at once VS sorting then merging
sorting func: merge_sort | merging func: merge_sorted_c
sort at once:       1.1942
sort, then merge:   0.5556
sorting func: merge_sort | merging func: merge_sorted_i
sort at once:       [Fail] merge_sort | merge_sorted_i -> maximum recursion depth exceeded while calling a Python object
sort, then merge:   0.5597
sorting func: merge_sort | merging func: merge_sorted_b
sort at once:       0.0095
sort, then merge:   0.5561
sorting func: merge_sort4 | merging func: merge_sorted_c
sort at once:       0.0411
sort, then merge:   0.0391
sorting func: merge_sort4 | merging func: merge_sorted_i
sort at once:       0.0386
sort, then merge:   0.0392
sorting func: merge_sort4 | merging func: merge_sorted_b
sort at once:       0.0116
sort, then merge:   0.0371
sorting func: merge_sort5 | merging func: merge_sorted_c
sort at once:       1.1825
sort, then merge:   0.0111
sorting func: merge_sort5 | merging func: merge_sorted_i
sort at once:       1.0720
sort, then merge:   0.0106
sorting func: merge_sort5 | merging func: merge_sorted_b
sort at once:       0.0136
sort, then merge:   0.0095
sorting func: _merge_sort5 | merging func: merge_sorted_c
sort at once:       0.0109
sort, then merge:   0.0126
sorting func: _merge_sort5 | merging func: merge_sorted_i
sort at once:       0.0110
sort, then merge:   0.0122
sorting func: _merge_sort5 | merging func: merge_sorted_b
sort at once:       0.0109
sort, then merge:   0.0109
sorting func: heap_sort | merging func: merge_sorted_c
sort at once:       0.0012
sort, then merge:   0.0043
sorting func: heap_sort | merging func: merge_sorted_i
sort at once:       0.0012
sort, then merge:   0.0038
sorting func: heap_sort | merging func: merge_sorted_b
sort at once:       0.0011
sort, then merge:   0.0026
sorting func: heap_sorti | merging func: merge_sorted_c
sort at once:       0.0010
sort, then merge:   0.0045
sorting func: heap_sorti | merging func: merge_sorted_i
sort at once:       0.0010
sort, then merge:   0.0041
sorting func: heap_sorti | merging func: merge_sorted_b
sort at once:       0.0011
sort, then merge:   0.0027
sorting func: bubble_sort | merging func: merge_sorted_c
sort at once:       0.8359
sort, then merge:   0.4090
sorting func: bubble_sort | merging func: merge_sorted_i
sort at once:       0.8357
sort, then merge:   0.4070
sorting func: bubble_sort | merging func: merge_sorted_b
sort at once:       0.8517
sort, then merge:   0.4046
** Sorting times...
function merge_sort (merge_sorted_c):   6.185883s
[FAIL] merge_sort (merge_sorted_i): ->  maximum recursion depth exceeded while calling a Python object
function merge_sort (merge_sorted_b):   0.061362s
function merge_sort4 (merge_sorted_c):  0.380683s
function merge_sort4 (merge_sorted_i):  0.354311s
function merge_sort4 (merge_sorted_b):  0.097866s
function merge_sort5 (merge_sorted_c):  6.110428s
function merge_sort5 (merge_sorted_i):  5.432237s
function merge_sort5 (merge_sorted_b):  0.075340s
function (builtin) sorted:              0.002491s
function _merge_sort5:                  0.092837s
function heap_sort:                     0.010843s
function heap_sorti:                    0.009808s
function bubble_sort:                   4.077386s
*** Test data consistency: OK
_test runs in: 37.5679 seconds
"""
