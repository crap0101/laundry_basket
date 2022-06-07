
from typing import Collection,Sequence,Iterable
from collections import deque
import importlib
import itertools
import timeit

###########
# DEFVALS #
###########

NESTED_TYPES = (Collection,Sequence,Iterable)
REC_TYPES = (str,bytes)
IGNORED_TYPES = ()

#######################
###### UTILITIES ######
#######################
    
def mklst_to_depth (depth=1000, length=10):
    l = [0,[1,1]]
    ll = l[-1]
    for i in range(depth):
        ll.append(list(range(length)))
        ll = ll[-1]
    return l

def _import_module (mod_name):
    try:
        m = importlib.import_module(mod_name)
        globals()[mod_name] = m
    except ModuleNotFoundError:
        m = None
    return m

#################
# EXTRA MODULES #
#################

HAVE_IT_UT = bool(_import_module('iteration_utilities'))
HAVE_PAN = bool(_import_module('pandas'))
HAVE_MAT = bool(_import_module('matplotlib'))
HAVE_MORE = bool(_import_module('more_itertools'))

###########################
# FLATTEN IMPLEMENTATIONS #
###########################

def dflatten (seq, ignore=IGNORED_TYPES, as_iter=False):
    """flat using deque"""
    def inner_flat (seq, ignore):
        d = deque(seq)
        while d:
            s = d.popleft()
            if isinstance(s, NESTED_TYPES):
                skip_ignored = isinstance(s, ignore)
                if isinstance(s, REC_TYPES):
                    if skip_ignored:
                        yield s
                    else:
                        for i in s:
                            yield i
                elif skip_ignored:
                    yield s
                else:
                    for item in reversed(s):
                        d.appendleft(item)
            else:
                yield s
    gen = inner_flat(seq, ignore)
    return gen if as_iter else list(gen)

def flatten (seq, ignore=IGNORED_TYPES, as_iter=False):
    """flat using list"""
    def inner_flat (seq, ignore):
        d = list(seq)
        while d:
            s = d.pop(0)
            if isinstance(s, NESTED_TYPES):
                skip_ignored = isinstance(s, ignore)
                if isinstance(s, REC_TYPES):
                    if skip_ignored:
                        yield s
                    else:
                        for i in s:
                            yield i
                elif skip_ignored:
                    yield s
                else:
                    for item in reversed(s):
                        d.insert(0, item)
            else:
                yield s
    gen = inner_flat(seq, ignore)
    return gen if as_iter else list(gen)

def iflatten (seq, ignore=IGNORED_TYPES):
    """deep-flat `seq` yielding items."""
    d = deque(seq)
    while d:
        s = d.popleft()
        if isinstance(s, NESTED_TYPES):
            skip_ignored = isinstance(s, ignore)
            if isinstance(s, REC_TYPES):
                if skip_ignored:
                    yield s
                else:
                    for i in s:
                        yield i
            elif skip_ignored:
                yield s
            else:
                d.extendleft(reversed(s))
        else:
            yield s


##################################
# OTHERS FLATTEN IMPLEMENTATIONS #
##################################
def flatten_cglacet (seq):
    """from: https://stackoverflow.com/a/51649649
    Tweaked a bit (REC_TYPES, etc)
    """
    def flatten(iterable):
        return list(items_from(iterable))
    def items_from(iterable):
        cursor_stack = [iter(iterable)]
        while cursor_stack:
            sub_iterable = cursor_stack[-1]
            try:
                item = next(sub_iterable)
            except StopIteration:   # post-order
                cursor_stack.pop()
                continue
            if is_list_like(item):  # pre-order
                cursor_stack.append(iter(item))
            elif item is not None:
                if isinstance(item, REC_TYPES):
                    for i in item:
                        yield i
                else:
                    yield item     # in-order
    def is_list_like(item):
        return (isinstance(item, NESTED_TYPES)
                and not isinstance(item, REC_TYPES))
    return flatten(seq)


#######################
def _example():
    def _exec(f, *args, **kw):
        if 'prepend' in kw:
            prepend = kw.pop('prepend')
        else:
            prepend=''
        print(f'----- {prepend}{f.__name__} ({kw}):')
        for i in f(*args, **kw):
            print(i, end=', ')
        print()
    ll = [range(10),1,2, "foo", [], ['a','b','c'], 3,4,[5,6,7,8],
          range(10),7,8,9,[10,11,[12,13,[14,15,[16,17],18,19],20,21],22],23]
    print('*** EXAMPLE:')
    print('** INPUT:')
    print(ll)
    _exec(iflatten,ll)
    _exec(iflatten,ll,ignore=(REC_TYPES))
    _exec(flatten,ll)
    _exec(dflatten,ll)
    _exec(flatten_cglacet,ll)
    if HAVE_IT_UT:
        _exec(iteration_utilities.deepflatten,ll)
    if HAVE_PAN:
        pf = pandas.core.common.flatten
        _exec(pf,ll,prepend=pf.__module__+'.')
    if HAVE_MAT:
        mp = matplotlib.cbook.flatten
        _exec(mp,ll,prepend=mp.__module__+'.')
    if HAVE_MORE:
        _exec(more_itertools.collapse,ll)


#######################
####### TESTS #########
#######################

def _test_it_ut(lst, r, fmt_report):
    I = REC_TYPES
    try:
        t = timeit.Timer('list(itu.deepflatten(lst, depth=10000, ignore=I))',
                         'from __main__ import iteration_utilities as itu', globals=locals()).timeit(r)
        print(fmt_report.format('deepflatten:', t/r))
    except RecursionError as e:
        print('[FAIL] deepflatten:', e)

def _test_pandas(lst, r, fmt_report):
    try:
        t = timeit.Timer('list(pandas.core.common.flatten(lst))',
                         'from __main__ import pandas', globals=locals()).timeit(r)
        print(fmt_report.format('pandas:', t/r))
    except RecursionError as e:
        print('[FAIL] pandas.core.common.flatten:', e)
        
def _test_matp(lst, r, fmt_report):
    try:
        t = timeit.Timer('list(matplotlib.cbook.flatten(lst))',
                         'from __main__ import matplotlib', globals=locals()).timeit(r)
        print(fmt_report.format('matplotlib:', t/r))
    except RecursionError as e:
        print('[FAIL] matplotlib.cbook.flatten:', e)

def _test_moreit(lst, r, fmt_report):
    try:
        t = timeit.Timer('list(mo.collapse(lst))',
                         'from __main__ import more_itertools as mo', globals=locals()).timeit(r)
        print(fmt_report.format('collapse:', t/r))
    except RecursionError as e:
        print('[FAIL] more_itertools.collapse:', e)

def _test_eq(depth=1000):
    print('*** Test eq:')
    l = mklst_to_depth(depth)
    funcs = (flatten, iflatten, dflatten)
    funcs_o = (flatten_cglacet,)
    # test these too, with proper (short) input
    funcs_argh = []
    if HAVE_IT_UT: funcs_argh.append(iteration_utilities.deepflatten)
    if HAVE_PAN: funcs_argh.append(pandas.core.common.flatten)
    if HAVE_MAT: funcs_argh.append(matplotlib.cbook.flatten)
    if HAVE_MORE:funcs_argh.append(more_itertools.collapse)
    ig = REC_TYPES
    for f1, f2 in itertools.combinations(funcs, 2):
        assert list(f1(l)) == list(f2(l)), f'[FAIL] {f1.__name__} <> {f2.__name__}'
        assert list(f1(l, ignore=ig)) == list(f2(l, ignore=ig)), f'[FAIL] {f1.__name__} <> {f2.__name__} (ignore=REC_TYPES)'
    print('assert eq: OK ({})'.format(','.join(f.__name__ for f in funcs)))
    ft = funcs[0]
    for f in funcs_o:
        assert list(f(l)) == list(ft(l)), f'[FAIL] {f.__name__} <> {ft.__name__}'
    print('assert eq: OK ({})'.format(','.join(f.__name__ for f in funcs_o)))
    l = mklst_to_depth(100)
    r0 = list(ft(l))
    for f in funcs_argh:
        assert r0 == list(f(l)), f'[FAIL] {f.__name__} <> {ft.__module__}.{ft.__name__}'
    print('assert eq: OK ({})'.format(','.join(f'{f.__module__}.{f.__name__}' for f in funcs_argh)))

def _test_times(depth=1000, repeats=100):
    print('*'*30)
    l = [0,[0,0,0]]
    l = mklst_to_depth(depth)
    r = repeats
    _report = '{:<18} {:.4f}s'
    print('*** Test times:')
    print(f'** config: list depth={depth} | repeats={repeats}')
    t = timeit.Timer('list(iflatten(l))', 'from __main__ import iflatten', globals=locals()).timeit(r)
    print(_report.format('iflatten:', t/r))
    t = timeit.Timer('flatten(l)', 'from __main__ import flatten', globals=locals()).timeit(r)
    print(_report.format('flatten:', t/r))
    t = timeit.Timer('dflatten(l)', 'from __main__ import dflatten', globals=locals()).timeit(r)
    print(_report.format('dflatten:', t/r))
    #################################
    t = timeit.Timer('flatten_cglacet(l)', 'from __main__ import flatten_cglacet', globals=locals()).timeit(r)
    print(_report.format('flatten_cglacet:', t/r))
    if HAVE_IT_UT:
        _test_it_ut(l, r, _report)
    if HAVE_PAN:
        _test_pandas(l, r, _report)
    if HAVE_MAT:
        _test_matp(l, r, _report)
    if HAVE_MORE:
        _test_moreit(l, r, _report)
    return

    ### Summary of unsuccessfully tests:
    # print(l)                    # RecursionError  ( ^L^ )
    # pandas.core.common.flatten  # RecursionError
    # matplotlib.cbook.flatten    # RecursionError
    # iteration_utilities         # RecursionError (recursion depth reached (?))
    # more_itertools.collapse     # RecursionError
    # numpy.ndarray.flat          # nope
    # numpy.ndarray.flatten       # nope
    
def _test(depth=1000, repeats=100):
    _test_eq(depth)
    _test_times(depth, repeats)


if __name__ == '__main__':
    _example()
    _test(repeats=20)
"""
crap0101@orange:~/test$ python3 deepflatten.py 
*** EXAMPLE:
** INPUT:
[range(0, 10), 1, 2, 'foo', [], ['a', 'b', 'c'], 3, 4, [5, 6, 7, 8], range(0, 10), 7, 8, 9, [10, 11, [12, 13, [14, 15, [16, 17], 18, 19], 20, 21], 22], 23]
----- iflatten ({}):
0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 2, f, o, o, a, b, c, 3, 4, 5, 6, 7, 8, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 
----- iflatten ({'ignore': (<class 'str'>, <class 'bytes'>)}):
0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 2, foo, a, b, c, 3, 4, 5, 6, 7, 8, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 
----- flatten ({}):
0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 2, f, o, o, a, b, c, 3, 4, 5, 6, 7, 8, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 
----- dflatten ({}):
0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 2, f, o, o, a, b, c, 3, 4, 5, 6, 7, 8, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 
----- flatten_cglacet ({}):
0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 2, f, o, o, a, b, c, 3, 4, 5, 6, 7, 8, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 
----- pandas.core.common.flatten ({}):
0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 2, foo, a, b, c, 3, 4, 5, 6, 7, 8, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 
----- matplotlib.cbook.flatten ({}):
0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 2, foo, a, b, c, 3, 4, 5, 6, 7, 8, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 
----- collapse ({}):
0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 2, foo, a, b, c, 3, 4, 5, 6, 7, 8, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 
*** Test eq:
assert eq: OK (flatten,iflatten,dflatten)
assert eq: OK (flatten_cglacet)
assert eq: OK (pandas.core.common.flatten,matplotlib.cbook.flatten,more_itertools.more.collapse)
******************************
*** Test times:
** config: list depth=1000 | repeats=20
iflatten:          0.0377s
flatten:           0.0416s
dflatten:          0.0393s
flatten_cglacet:   0.0437s
[FAIL] pandas.core.common.flatten: maximum recursion depth exceeded in comparison
[FAIL] matplotlib.cbook.flatten: maximum recursion depth exceeded while calling a Python object
[FAIL] more_itertools.collapse: maximum recursion depth exceeded in __instancecheck__
"""

"""
crap0101@orange:~/test$ ./PY3ENV/bin/python deepflatten.py
[... OMITTED OUTPUT ...]
*** Test eq:
assert eq: OK (flatten,iflatten,dflatten)
assert eq: OK (flatten_cglacet)
assert eq: OK (iteration_utilities.deepflatten)
******************************
*** Test times:
** config: list depth=1000 | repeats=20
iflatten:          0.0375s
flatten:           0.0414s
dflatten:          0.0392s
flatten_cglacet:   0.0424s
[FAIL] deepflatten: `deepflatten` reached maximum recursion depth.
"""

# less depth:
"""
[... OMITTED OUTPUT ...]
*** Test eq:
assert eq: OK (flatten,iflatten,dflatten)
assert eq: OK (flatten_cglacet)
assert eq: OK (pandas.core.common.flatten,matplotlib.cbook.flatten,more_itertools.more.collapse)
******************************
*** Test times:
** config: list depth=700 | repeats=20
iflatten:          0.0264s
flatten:           0.0294s
dflatten:          0.0276s
flatten_cglacet:   0.0306s
pandas:            0.3669s
matplotlib:        0.3314s
collapse:          0.4260s
"""
