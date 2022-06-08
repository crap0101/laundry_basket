
import argparse
import builtins
from collections import deque
import importlib
import itertools
import timeit
import typing
from typing import Collection, Sequence, Iterable

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

def _check_cmdline (parser, namespace):
    if namespace.DEPTH < 0:
        parser.error('constrain violation: DEPTH < 0')
    if namespace.REPEATS < 1:
        parser.error('constrain violation: REPEATS < 1')

def _import_module (mod_name):
    try:
        m = importlib.import_module(mod_name)
        globals()[mod_name] = m
    except ModuleNotFoundError:
        m = None
    return m

def _import_types (type_names, module_names):
    ret = []
    err_imp = None
    err_att = None
    for t in type_names:
        if not isinstance(t, str):
            # if not a string of a (possibly) type name, assuming already a type
            ret.append(t)
            continue
        for m in module_names:
            try:
                if isinstance(m, str):
                    mod = importlib.import_module(m)
                else:
                    # assuming already a module
                    mod = m
                ty = getattr(mod, t)
                ret.append(ty)
                break
            except ImportError as i:
                err_imp = i
            except AttributeError as a:
                err_att = a
        else:
            if err_imp:
                raise ImportError(err_imp)
            elif err_att:
                raise AttributeError(err_att)
            raise AttributeError('BUG! Should not be here!!!')
    return ret

def _set_defval (namespace):
    if isinstance(namespace, argparse.Namespace):
        try:
            kv = namespace.__dict__
        except AttributeError:
            kv = dict(namespace._get_kwargs())
    else:
        kv = namespace    
    for k,v in kv.items():
        globals()[k] = v

####################################
# EXTRA MODULES and DEFAULT VALUES #
####################################

_DEFVALS = {
    'NESTED_TYPES': (Collection,Sequence,Iterable,),
    'REC_TYPES': (str,bytes,),
    'IGNORED_TYPES': (),
    'DEPTH': 1000,
    'REPEATS': 100,}
_set_defval(_DEFVALS)

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


############
# EXAMPLES #
############

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
    _exec(iflatten,ll,ignore=REC_TYPES)
    _exec(iflatten,ll,ignore=IGNORED_TYPES)
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

###################
# CMDLINE PARSING #
###################

def get_parser(config):
    ep = 'NOTE: using -sre option may change tests behaviour, till to fail.'
    p = argparse.ArgumentParser(epilog=ep)
    p.add_argument('-d', '--depth', dest='DEPTH', type=int, default=config['DEPTH'],
                   metavar='N', help="depth for nested lists. Default:(%(default)s)")
    p.add_argument('-R', '--repeats', dest='REPEATS', type=int, default=config['REPEATS'],
                   metavar='N', help='timeit repeats times. Default:(%(default)s)')
    p.add_argument('-s', '--stype', dest='NESTED_TYPES', default=config['NESTED_TYPES'],
                   nargs='+',
                   help=('type names to be considered sequence to iterate on. '
                         'Builtin tipyes or '
                         'something from the typing or collections.abc modules. '
                         'Default: (%(default)s)'))
    p.add_argument('-r', '--rtype', dest='REC_TYPES', default=config['REC_TYPES'],
                   nargs='+',
                   help=('recursive type names to be treat specially (to avoid infinite loop). '
                         'Something from the typing or collections.abc modules. '
                         'Default: (%(default)s)'))
    p.add_argument('-e', '--exclude', dest='IGNORED_TYPES', default=config['IGNORED_TYPES'],
                   nargs='+',
                   help=('type names to be ignored (will not be flatted). '
                         'Default: (%(default)s)'))
    p.add_argument('-E', '--example', dest='__config_example', action='store_true',
                   help="Run a short example of outputs. Default:(%(default)s)")
    p.add_argument('-n', '--no-test', dest='__config_no_test', action='store_true',
                   help="Do not run tests. Default:(%(default)s)")
    return p
    

if __name__ == '__main__':
    p = get_parser(_DEFVALS)
    namespace = p.parse_args()
    _check_cmdline(p, namespace)
    # if custom type names were passed at commandline, check and set them
    typeslist = list(name for name,args in _DEFVALS.items() if name.endswith('_TYPES'))
    _d = namespace.__dict__
    for name in typeslist:
        t = _d[name]
        tt = _import_types(t, ('builtins', 'typing'))
        _d[name] = tuple(tt)
    # set globally the namespace - for keys in _DEFVALS (only these right now)
    # XXX+TODO: exclude foreign option-variables, when/if added in the parser)
    # UPDATE: choose to namese these variale as __config_{name}
    _set_defval(namespace)
    if namespace.__config_example:
        _example()
    if not namespace.__config_no_test:
        _test(namespace.DEPTH, namespace.REPEATS)


"""
crap0101@orange:~/test$ python3 deepflatten.py -R 10 -E
*** EXAMPLE:
** INPUT:
[range(0, 10), 1, 2, 'foo', [], ['a', 'b', 'c'], 3, 4, [5, 6, 7, 8], range(0, 10), 7, 8, 9, [10, 11, [12, 13, [14, 15, [16, 17], 18, 19], 20, 21], 22], 23]
----- iflatten ({}):
0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 2, f, o, o, a, b, c, 3, 4, 5, 6, 7, 8, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 
----- iflatten ({'ignore': (<class 'str'>, <class 'bytes'>)}):
0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 2, foo, a, b, c, 3, 4, 5, 6, 7, 8, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 
----- iflatten ({'ignore': ()}):
0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 2, f, o, o, a, b, c, 3, 4, 5, 6, 7, 8, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 
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
** config: list depth=1000 | repeats=10
iflatten:          0.0375s
flatten:           0.0402s
dflatten:          0.0383s
flatten_cglacet:   0.0424s
[FAIL] pandas.core.common.flatten: maximum recursion depth exceeded in comparison
[FAIL] matplotlib.cbook.flatten: maximum recursion depth exceeded while calling a Python object
[FAIL] more_itertools.collapse: maximum recursion depth exceeded in __instancecheck__
crap0101@orange:~/test$ python3 deepflatten.py -R 10 -En -e list
*** EXAMPLE:
** INPUT:
[range(0, 10), 1, 2, 'foo', [], ['a', 'b', 'c'], 3, 4, [5, 6, 7, 8], range(0, 10), 7, 8, 9, [10, 11, [12, 13, [14, 15, [16, 17], 18, 19], 20, 21], 22], 23]
----- iflatten ({}):
0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 2, f, o, o, a, b, c, 3, 4, 5, 6, 7, 8, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 
----- iflatten ({'ignore': (<class 'str'>, <class 'bytes'>)}):
0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 2, foo, a, b, c, 3, 4, 5, 6, 7, 8, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 
----- iflatten ({'ignore': (<class 'list'>,)}):
0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 2, f, o, o, [], ['a', 'b', 'c'], 3, 4, [5, 6, 7, 8], 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 7, 8, 9, [10, 11, [12, 13, [14, 15, [16, 17], 18, 19], 20, 21], 22], 23, 
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
crap0101@orange:~/test$ python3 deepflatten.py -R 10 -d 700 # let failing functions to terminate
*** Test eq:
assert eq: OK (flatten,iflatten,dflatten)
assert eq: OK (flatten_cglacet)
assert eq: OK (pandas.core.common.flatten,matplotlib.cbook.flatten,more_itertools.more.collapse)
******************************
*** Test times:
** config: list depth=700 | repeats=10
iflatten:          0.0264s
flatten:           0.0283s
dflatten:          0.0270s
flatten_cglacet:   0.0301s
pandas:            0.3640s
matplotlib:        0.3299s
collapse:          0.4399s
"""

# runs in a virtual environment for testing iteration_utilities module:
"""
crap0101@orange:~/test$ ./PY3ENV/bin/python deepflatten.py -R 10 
*** Test eq:
assert eq: OK (flatten,iflatten,dflatten)
assert eq: OK (flatten_cglacet)
assert eq: OK (iteration_utilities.deepflatten)
******************************
*** Test times:
** config: list depth=1000 | repeats=10
iflatten:          0.0372s
flatten:           0.0410s
dflatten:          0.0385s
flatten_cglacet:   0.0420s
[FAIL] deepflatten: `deepflatten` reached maximum recursion depth.
crap0101@orange:~/test$ ./PY3ENV/bin/python deepflatten.py -R 10 -d 900 # let failing functions to terminate
*** Test eq:
assert eq: OK (flatten,iflatten,dflatten)
assert eq: OK (flatten_cglacet)
assert eq: OK (iteration_utilities.deepflatten)
******************************
*** Test times:
** config: list depth=900 | repeats=10
iflatten:          0.0337s
flatten:           0.0365s
dflatten:          0.0349s
flatten_cglacet:   0.0388s
deepflatten:       0.0029s
"""
