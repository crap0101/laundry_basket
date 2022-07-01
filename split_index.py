# Python 3.8.10
# Cfr. https://forum.ubuntu-it.org/viewtopic.php?f=33&t=649821

import itertools
from typing import Iterator, List, Sequence

fakelist = range(20)
indexes = [3,5,7,9,15]

def split_at (seq: Sequence, indexes: Sequence[int]) -> Iterator[List]:
    """Yields Lists splitting $seq at the given $indexes.
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
    """
    def keyfunc (lst):
        def _next(seq):
            try:
                return next(seq)
            except StopIteration:
                return float('+inf')
        iter_lst = iter(lst)
        item = _next(iter_lst)
        call_count = itertools.count()
        def aux (value):
            nonlocal item
            idx = next(call_count)
            if idx > item:
                item = _next(iter_lst)
            return item
        return aux
    for _, islice in itertools.groupby(seq, key=keyfunc(indexes)):
        yield list(islice)

def _test():
    from random import randint as r
    fakelist = range(20)
    indexes = [3,5,7,9,15]
    print('*** Example:')
    print('fakelist:', list(fakelist))
    print('indexes:', indexes)
    for lst in split_at(fakelist, indexes):
        print(lst)
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
    if sys.argv[1:] and sys.argv[1] == '-t':
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
