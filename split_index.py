# Python 3.8.10
# Cfr. https://forum.ubuntu-it.org/viewtopic.php?f=33&t=649821

import itertools
import operator
from typing import Iterator, List, Sequence

fakelist = range(20)
indexes = [3,5,7,9,15]

def split_at (seq: Sequence, indexes: Sequence[int], where='after') -> Iterator[List]:
    """Yields Lists splitting $seq at the given $indexes.
    $where must be 'at' which split like normal python slicing list[a:where]
    or 'after' (default) splitting *after* the given index.
    >>> list(split_at(range(18), [2,4,8,15]))
    [[0, 1, 2], [3, 4], [5, 6, 7, 8], [9, 10, 11, 12, 13, 14, 15], [16, 17]]
    >>> list(split_at(range(7), [2,4,8,15]))
    [[0, 1, 2], [3, 4], [5, 6]]
    >>> # $indexes should be a sequence of integers in range 0..n
    >>> # cuz negative indexes may lead to unexpected results (obviously).
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


def _example():
    fakelist = range(20)
    indexes = [3,5,7,9,15]
    print('*** Example:')
    print('fakelist:', list(fakelist))
    print('indexes:', indexes)
    for lst in split_at(fakelist, indexes):
        print(lst)

def _test():
    from random import randint as r
    _example()
    print('*** Test splitting: ', end='')
    for _ in range(100):
        pieces = list(filter(None, [list(range(1, r(1,30)))
                                    for __ in range(5, r(10,20))]))
        _i = list(map(len, pieces));_i[0]-=1
        # ^^^ remove empty list and set index properly for reconstruction
        # (since split_at split *after* index $n and len(item) would be +1
        # for every next item.
        indexes = list(itertools.accumulate(_i))
        total = list(itertools.chain.from_iterable(pieces))
        res = list(split_at(total, indexes))
        assert res == pieces, f'[FAIL]: {pieces} != {res} | {indexes}'
    # test other seqs:
    triplets = [
        ([], [2,4,6], []),
        ([], [0,2,4,6], []),
        ([1], [2,4,6], [[1]]),
        ([1], [0,2,4,6], [[1]]),
    ]
    for lst, indexes, res in triplets:
        assert list(split_at(lst, indexes)) == res, f'[FAIL]: {lst} != {res}'
    print('OK')

if __name__ == '__main__':
    import sys
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('-t', '--test', dest='test', action='store_true',
                 help='Run tests.')
    args = p.parse_args()
    if args.test:
        _test()


"""
crap0101@orange:~/test$ python3 split_index.py -t
*** Example:
fakelist: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
indexes: [3, 5, 7, 9, 15]
[0, 1, 2, 3]
[4, 5]
[6, 7]
[8, 9]
[10, 11, 12, 13, 14, 15]
[16, 17, 18, 19]
*** Test splitting: OK
"""

""" # note: numpy.array_split splits before the given index
>>> import numpy as np
>>> r = 100
>>> inarr = range(1000000)
>>> idx = list(range(1,1000000, 10))
>>> timeit.Timer(stmt='list(split_at(inarr, idx))', setup='from __main__ import split_at, np', globals=locals()).timeit(r) / r
0.398804909074679
>>> timeit.Timer(stmt='list(np.array_split(inarr, idx))', setup='from __main__ import split_at, np', globals=locals()).timeit(r) / r
0.5443526016920806
"""
