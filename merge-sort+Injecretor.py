#!/usr/bin/env python3
# >= 3.8.10

from collections.abc import Sequence
from itertools import zip_longest as izip

def merge_sort (s1: Sequence, s2: Sequence) -> Sequence:
    """Merge two ordered sequences returning a third."""
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

        
class Injecretor:
    """Like an iterator, better than an iterator :-D
    0. can insert multiple value to be yielded while looping on it
    1. can retreave the last yielded value (userful in some circustances)
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


def merge_sort_g (s1: Sequence, s2: Sequence) -> Sequence:
    """Merge two ordered sequences returning a third."""
    g1 = Injecretor(s1,name='s1')
    g2 = Injecretor(s2,name='s2')
    for i, j in izip(g1, g2, fillvalue=None):
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

def _test (func1, func2, argslist):
    for args in argslist:
        r1 = list(func1(*args))
        r2 = list(func2(*args))
        assert r1 == r2, 'ERR: {} != {}'.format(r1, r2)

if __name__ == '__main__':
    inputs = [([],[]), ([], range(5)), (range(9),[]),
        (range(10), range(5,15)),
        (range(6,12), range(5)),
        (range(10), range(2,6)),
        (range(2,6), range(10)),
    ]
    if 0: # well...
        _test(merge_sort, merge_sort_g, inputs)
    for lsts in inputs:
        print('------\n[MS]  input: {0[0]} {0[1]} -> {1}'.format(
            lsts, merge_sort(*lsts)))
        print('[MSG] input: {0[0]} {0[1]} -> {1}'.format(
            lsts, list(merge_sort_g(*lsts))))


"""
crap0101@orange:~/test$ python3 merge-sort.py 
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
