# Python 3.8.10
# Cfr. https://forum.ubuntu-it.org/viewtopic.php?f=33&t=649821
#
# author: Marco Chieppa | crap0101
#

import itertools
import operator
from typing import Iterator, List, Sequence


def split_at (seq: Sequence, indexes: Sequence[int], where='after') -> Iterator[List]:
    """Yields Lists splitting $seq at the given $indexes.
    $where must be 'at' which split like normal python slicing list[a:where]
    or 'after' (default) splitting *after* the given index.
    >>> list(split_at(range(18), [2,4,8,15]))
    [[0, 1, 2], [3, 4], [5, 6, 7, 8], [9, 10, 11, 12, 13, 14, 15], [16, 17]]
    >>> list(split_at(range(7), [2,4,8,15]))
    [[0, 1, 2], [3, 4], [5, 6]]
    >>> # $indexes should be a sequence of *distinct* sorted integers
    >>> #in range 0..n cuz negative indexes ore repeated ones may lead
    >>> to unexpected results (obviously).
    >>> list(split_at(range(9), [-1,2,4,6])) 
    [[0, 1, 2], [3, 4], [5, 6], [7, 8]]
    >>> list(split_at(range(9), [-1,-2,4,6]))
    [[0], [1, 2, 3, 4], [5, 6], [7, 8]]
    >>> list(split_at(range(17), [2,4,-8,15]))
    [[0, 1, 2], [3, 4], [5], [6, 7, 8, 9, 10, 11, 12, 13, 14, 15], [16]]
    >>> list(split_at(range(10), range(0, 10, 2)))
    [[0], [1, 2], [3, 4], [5, 6], [7, 8], [9]]
    >>> list(split_at(range(10), range(0, 10, 2), where='at'))
    [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]
    >>> list(split_at(range(11), [2,5,5,7], where='at'))
    [[0, 1], [2, 3, 4, 5], [6], [7, 8, 9, 10]]
    >>> list(split_at(range(11), [7,4,3], where='at'))
    [[0, 1, 2, 3, 4, 5, 6], [7], [8], [9, 10]]
    """
    if where == 'after':
        compare = operator.gt
    elif where == 'at':
        compare = operator.ge
    else:
        raise ValueError(f'wrong value for "where": "{where}"')
    def keyfunc (lst):
        iter_lst = iter(lst)
        item = next(iter_lst, float('+inf'))
        call_count = itertools.count()
        def aux (value):
            nonlocal item
            idx = next(call_count)
            if compare(idx, item):
                item = next(iter_lst, float('+inf'))
            return item
        return aux
    for _, islice in itertools.groupby(seq, key=keyfunc(indexes)):
        yield list(islice)


def _split_at_with_axe (seq, idxs):
    lst = list(seq)
    head = 0
    arr = []
    if not idxs:
        return [lst]
    for tail in idxs:
        arr.append(lst[head:tail])
        head = tail
    end = lst[tail:]
    if end:
        arr.append(end)
    return arr

def _example():
    fakelist = range(20)
    indexes = [3,5,7,9,15]
    print('*** Example:')
    print('fakelist:', list(fakelist))
    print('indexes:', indexes)
    for lst in split_at(fakelist, indexes):
        print(lst)

def _test_split():
    from random import randint as r
    print('*** Test splitting: ', end='')
    for _ in range(100):
        pieces = list(filter(None, [list(range(1, r(1,30)))
                                    for __ in range(5, r(10,20))]))
        _i = list(map(len, pieces))
        _ii = list(map(len, pieces))
        _i[0]-=1
        # ^^^ remove empty list and set index properly for reconstruction
        # (since split_at split *after* index $n and len(item) would be +1
        # for every next item.
        indexes = list(itertools.accumulate(_i))
        total = list(itertools.chain.from_iterable(pieces))
        res = list(split_at(total, indexes))
        assert res == pieces, f'[FAIL]: {pieces} != {res} | {indexes}'
        # at
        indexes = list(itertools.accumulate(_ii))
        res = list(split_at(total, indexes, where='at'))
        assert res == pieces, f'[FAIL]:(at): {pieces} != {res} | {indexes}'
    # test other seqs:
    triplets = [
        ([], [2,4,6], []),
        ([], [0,2,4,6], []),
        ([1], [2,4,6], [[1]]),
        ([1], [0,2,4,6], [[1]]),
    ]
    for lst, indexes, res in triplets:
        assert list(split_at(lst, indexes)) == res, f'[FAIL]: {lst} != {res}'
        assert list(split_at(lst, indexes, 'at')) == res, f'[FAIL]: {lst} != {res}'
    print('OK')

def _test_cmp():
    """compare with others methods:
    0. numpy.split_at
    * It produces empty seqs when splitting at the first or last index.
    * conversely split_at doesn't. These are interesting and sobering behavior,
    * a matter of choice about what is a split and how to interpret it.
    * For split_at I choose to not consider before the head of after the tail
    * (and so producing empty list) a real split.
    >>> list(split_at(range(10), [10], where='at'))
    [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]]
    >>> list(np.array_split(range(10), [10]))
    [array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]), array([], dtype=int64)]
    * Anothers thing worthy of reasoning is the case of unsorted indexes:
    >>> list(split_at(range(10), [7,4,3], where='at'))
    [[0, 1, 2, 3, 4, 5, 6], [7], [8], [9]]
    >>> list(np.array_split(range(10), [7,4,3]))
    [array([0, 1, 2, 3, 4, 5, 6]), array([], dtype=int64), array([], dtype=int64), array([3, 4, 5, 6, 7, 8, 9])]
    * and also that of repeated indexes:
    >>> list(split_at(range(10), [3,5,5], where='at'))
    [[0, 1, 2], [3, 4, 5], [6, 7, 8, 9]]
    >>> list(np.array_split(range(10), [3,5,5]))
    [array([0, 1, 2]), array([3, 4]), array([], dtype=int64), array([5, 6, 7, 8, 9])]
    """
    from random import randint as r
    import numpy as np
    print('*** Test compare')
    print('* compare with numpy.array_split: ', end='')
    llen = 1000
    for _ in range(100):
        lst = list(range(llen))
        # unique and sorted indexes, for the reasons written in the docstring
        indexes = sorted(set(r(0, llen) for _ in range(r(0,500))))
        s1 = list(split_at(lst, indexes, 'at'))
        s2 = list(list(x) for x in np.array_split(lst, indexes) if x.size)
        assert s1 == s2, f'''[FAIL] split_at: {s1}
!= numpy.array_split: {s2}
indexes: {indexes}'''
    print('OK')
    print('* compare with _split_at_with_axe: ', end='')
    for _ in range(100):
        lst = list(range(llen))
        # unique and sorted indexes, for the reasons written in the docstring
        indexes = sorted(set(r(0, llen) for _ in range(r(0,500))))
        s1 = list(split_at(lst, indexes, 'at'))
        s2 = list(list(x) for x in _split_at_with_axe(lst, indexes) if x)
        assert s1 == s2, f'''[FAIL] split_at: {s1}
!= _split_at_with_axe: {s2}
indexes: {indexes}'''
    print('OK')
    
def _test_time():
    import timeit
    from random import randint as r 
    from numpy import array_split
    print('*** Test times')
    llen = r(10, 1000000)
    lst = list(range(llen))
    indexes = sorted(set(r(0, llen) for _ in range(r(0,llen))))
    setup = 'from __main__ import split_at, _split_at_with_axe'
    stmt = '{}(lst, indexes)'
    rep = 50
    report = '{:<20}: {:.4f}s'
    loc = locals()
    print(f'(list len = {llen} | indexes = {len(indexes)} | repeats = {rep})')
    time = timeit.Timer('list(split_at(lst, indexes, where="at"))', setup, globals=loc).timeit(rep) / rep
    print(report.format('split_at', time))
    time = timeit.Timer(stmt.format('_split_at_with_axe'), setup, globals=loc).timeit(rep) / rep
    print(report.format('_split_at_with_axe', time))
    time = timeit.Timer(stmt.format('array_split'), setup, globals=loc).timeit(rep) / rep
    print(report.format('array_split', time))

def _test():
    _test_split()
    _test_cmp()
    _test_time()

if __name__ == '__main__':
    import sys
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('-t', '--test', dest='test', action='store_true',
                 help='Run tests.')
    p.add_argument('-e', '--example', dest='example', action='store_true',
                 help='Run example.')
    args = p.parse_args()
    if args.example:
        _example()
    if args.test:
        _test()


"""
crap0101@orange:~/test$ python3 split_index.py -e
*** Example:
fakelist: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
indexes: [3, 5, 7, 9, 15]
[0, 1, 2, 3]
[4, 5]
[6, 7]
[8, 9]
[10, 11, 12, 13, 14, 15]
[16, 17, 18, 19]
crap0101@orange:~/test$ python3 split_index.py -t
*** Test splitting: OK
*** Test compare
* compare with numpy.array_split: OK
* compare with _split_at_with_axe: OK
*** Test times
(list len = 664906 | indexes = 18105 | repeats = 50)
split_at            : 0.2244s
_split_at_with_axe  : 0.0345s
array_split         : 0.1239s
crap0101@orange:~/test$ python3 split_index.py -t
*** Test splitting: OK
*** Test compare
* compare with numpy.array_split: OK
* compare with _split_at_with_axe: OK
*** Test times
(list len = 598331 | indexes = 232487 | repeats = 50)
split_at            : 0.4121s
_split_at_with_axe  : 0.1150s
array_split         : 0.7606s
"""
