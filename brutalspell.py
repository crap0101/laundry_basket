#!/usr/bin/env python
# -*- coding: utf-8 -*-
# A brutal spell checker

# Copyright (C) 2026  Marco Chieppa | crap0101

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not see <http://www.gnu.org/licenses/>

from __future__ import annotations # for annotation of Trie in the class itself
from collections.abc import Iterable, Sequence
import json
from typing import Any, Union

__doc__ = '''Brutal spell checker.'''

Seq = Sequence | Iterable
Str = str | bytes


class BrutalSpellError(Exception):
    """Base error class for brutal errors."""
    def __init__ (self, msg):
        self.msg = msg
        super().__init__(msg)
    def __str__ (self):
        return self.msg


class BrutalSpellDataError(BrutalSpellError):
    """Brutal errors around data."""
    pass

class BrutalSpellDecodeError(BrutalSpellError):
    """json problems."""
    pass

class BrutalSpell:
    """A brutal spell checker object."""
    def __init__ (self,
                  data_or_file: Seq|Str = None,
                  rawfile: bool = False,
                  use_set: bool = False):
        """
        Loads the brutal spell checker.
        *data_or_file* are optional data (a word, a sequence of words, default None)
        to be loaded and therefore used to check spelling.
        If *data_or_file* is a single Str, considers it as a path to some
        json-formatted file to load UNLESS *rawfile* is a true value, in which case
        it is considered as a file with a list of words (one per line).
        If *use_set* is True, uses a set() for internal storage instead of a Trie.
        """
        self._fromfile = isinstance(data_or_file, Str)
        self._rawfile = bool(rawfile)
        self._init_data = data_or_file if self._fromfile else None
        self._use_set = bool(use_set)
        self._data = set() if self._use_set else Trie()
        if self._init_data:
            if self._fromfile:
                self.load(data_or_file, self._rawfile)
            else:
                self.add(data_or_file)

    def __len__ (self) -> int:
        """Returns the number of current words."""
        return len(self._data)

    def add (self,
             word_or_seq: Str|Seq,
             writeonfile: bool = False,
             otherfile: Str|bool = None) -> None:
        """
        Adds *word_or_seq* to the internal set of words used for spell checking.
        If *writeonfile* is a true value, write out the updated set in the path
        indicated by the *data_or_file* argument of the __init__ UNLESS you
        provide the *otherfile* argument, which must be a filepath in which
        the write will be happen.
        """
        if isinstance(word_or_seq, Str):
            self._data.add(word_or_seq)
        else:
            self._data.update(word_or_seq)
        if writeonfile:
            self.write(otherfile)

    def check (self, word: Str) -> bool:
        """
        Returns True if *word* is in the internal set of words.
        """
        return word in self._data

    def get_data (self) -> tuple[Str, ...]:
        """
        Returns a copy of the internal data set, as a tuple.
        """
        return tuple(self._data)

    def load (self,
              data: Str,
              rawfile: bool = False,
              set_default = False) -> None:
        """
        Loads *data*, a filepath to some json-formatted file UNLESS *rawfile* is a
        true value, in which case considers it a file with a list of words (one per
        line) to load. If *set_default* is a true value, sets this file as the
        default one for writing out the internal data set (used by the write()
        method), overwriting the possible filepath used at the time of the object
        instantiation (the __init__'s *data_or_file* argument).
        """
        if rawfile:
            with open(data) as f:
                d = set(filter(None, (w.strip() for w in f)))
        else:
            with open(data) as f:
                try:
                    d = json.load(f)
                except json.decoder.JSONDecodeError:
                    raise BrutalSpellDecodeError(f"Cant load from '{data}': not a json file?")
        self.add(d)
        if set_default:
            self._fromfile = True
            self._rawfile = bool(rawfile)
            self._init_data = data

    def write (self, otherfile: Str|bool = None) -> None:
        """
        Tries to write out the updated set in the path indicated by the *data_or_file*
        argument of the __init__ (or the last one possibly used in the load() method).
        If wasn't a filepath throws an error, UNLESS you provide the *otherfile* argument,
        which must be a path to file in which the write will be happens.
        Throws a BrutalSpellDataError if the default value is not a filepath. 
        NOTE: if *otherfile* is not provided and the default path is a non-json file,
        the old file content will to be ERASED and REPLACED with the json representation
        of the ACTUAL object's set of data, something which you probably want to avoid.
        """
        if not otherfile:
            if not self._fromfile:
                raise BrutalSpellDataError("data not loaded from file, can't write out!")
            with open(self._init_data, 'w') as out:
                json.dump(tuple(self._data), out)
        else:
            with open(otherfile, 'w') as out:
                json.dump(tuple(self._data), out)


class Trie:
    def __init__(self, seq: Seq = (), rec: bool = True):
        """
        Initializes the trie, with the optional sequence *seq*.
        *rec* is a directive for using recursive methods in some operations
        which are generally fasters but with known issues; default to True,
        should be safe for general uses (affetcs: __contains__, __iter__,
        iter, search, tolist).
        """
        # private attributes:
        self._size = 0
        self._rec = bool(rec)
        # methods defined after self.recursive:
        self.iter = None
        self.search = None
        self.tolist = None
        # public properties and attributes:
        self.END = False
        self.recursive = self._rec
        self.subt = {}
        if seq:
            self.add(seq)

    def __contains__ (self, seq: Seq) -> bool:
        """Returns True if *seq* belongs to this trie."""
        return self.search(seq)
    def __getitem__ (self, element: Any) -> Trie:
        """Returns the sub-trie associated at the *element* key."""
        return self.subt[element]
    def __setitem__ (self, element: Any, v: Trie) -> None:
        """Sets the value *v* (must be a Trie) for the *element* key."""
        self.subt[element] = v

    def __iter__ (self) -> Iterable[Any]:
        """Yields sequences from this Trie."""
        return self.iter()
    def iter (self):
        """
        Yields sequences from this Trie.
        Placeholder, assigned to the proper method in the __init__.
        """
        raise NotImplementedError
    def _iter_it (self):
        # iterative
        for k in Trie.trie_to_list_it(self):
            yield k
    def _iter_rec (self):
        # recursive
        for k in Trie.trie_to_list_rec(self):
            yield k

    def __len__ (self) -> int:
        """Returns the number of sequences of this Trie."""
        return self._size
        # NOTE: slower iterative method follow.
        #       The recursive one was ~ 2x faster but not
        #       as fast as update the size dinamically.
        # def len (self):
        #     tries = [self]
        #     tot = 0
        #     while tries:
        #         t = tries.pop()
        #         tot += t.END
        #         tries.extend(t[k] for k in t.keys())
        #     return tot

    def add (self, seq: Seq) -> None:
        """Adds *seq* to this Trie."""
        t = self
        for e in seq:
            if e not in t.keys():
                t[e] = Trie()
            t = t[e]
        if not t.END:
            t.END = True
            self._size += 1

    def keys (self) -> Any:
        """Yields the keys of this Trie."""
        for k in self.subt:
            yield k

    @property
    def recursive (self):
        return self._rec
    @recursive.setter
    def recursive (self, value: bool):
        self._rec = bool(value)
        if not self._rec:
            self.search = self._search_it
            self.iter = self._iter_it
            self.tolist = self._tolist_it
        else:
            self.search = self._search_rec
            self.iter = self._iter_rec
            self.tolist = self._tolist_rec

    def search (self, seq: Any):
        """
        Returns True if *seq* is in this trie.
        Placeholder, assigned to the proper method in the __init__.
        """
        raise NotImplementedError
    def _search_it (self, seq: Any) -> bool:
        # iterative method
        """
        Returns True if *seq* is in this trie.
        This is the Iterative version, slower but more safe.
        """
        return Trie.trie_search_it(self)
    def _search_rec (self, seq: Any) -> bool:
        # recursive method
        """
        Returns True if *seq* is in this trie.
        """
        return Trie.trie_search_rec(self, seq)
    @staticmethod
    def trie_search_it (trie: Trie, seq: Any) -> bool:
        # iterative
        """
        Returns True if *seq* is in *trie*.
        This is the Iterative version, slower but more safe.
        """
        t = trie
        for e in seq:
            if e not in t.keys():
                return False
            t = t[e]
        return t.END
    @staticmethod
    def trie_search_rec (trie: Trie, seq: Seq) -> bool:
        # recursive
        """Returns True if *trie* contains *seq*."""
        if not seq:
            if trie.END:
                return True
            return False
        try:
            c = seq[0]
        except TypeError:
            try:
                c = next(seq)
            except StopIteration:
                return False
        try:
            return Trie.trie_search_rec(trie[c], seq[1:])
        except TypeError:
            return Trie.trie_search_rec(trie[c], c)
        except KeyError:
            return False

    def tolist (self) -> list[Any]:
        """
        Returns the sequences of this Trie as a list.
        Placeholder, assigned to the proper method in the __init__.
        """
        raise NotImplementedError
    def _tolist_it (self) -> list[Any]:
        return Trie.trie_to_list_it(self)
    def _tolist_rec (self) -> list[Any]:
        return Trie.trie_to_list_rec(self)
    @staticmethod
    def trie_to_list_it (trie: Trie) -> list[Any]:
        # iterative
        """
        Returns the sequences of *trie* as a list.
        """
        total = []
        stack = [[trie, []]]
        while stack:
            t, lst = stack.pop()
            for k in t.keys():
                if t[k].END:
                    total.append(lst + [k])
                stack.append([t[k], lst + [k]])
        return total
    @staticmethod
    def trie_to_list_rec (trie: Trie) -> list[Any]:
        # recursive
        """
        Returns the sequences of *trie* as a list.
        """
        def ttlr (trie, pw=[]):
            s = []
            if trie.END:
                s.append(pw)
            for k in trie.keys():
                s.extend([e for e in ttlr(trie[k], pw + [k])])
            return s
        return ttlr(trie)

    def update (self, seq: Seq[Seq, ...]) -> None:
        """Adds the sequences in the *seq* sequence to this Trie."""
        for s in seq:
            self.add(s)
    #####
    #XXX: add remove()
    #####

class WTrie (Trie):
    """A words's specialized Trie."""
    def __init__(self, word: Str = (), rec: bool = True):
        super().__init__(word, rec)

    def __iter__ (self) -> Iterable[Str]:
        """Yields words from this Trie."""
        for k in self.iter():
            yield ''.join(k)

    def _tolist_it (self):
        return list(''.join(e) for e in super()._tolist_it())
    def _tolist_rec (self):
        return list(''.join(e) for e in super()._tolist_rec())





""" EXAMPLES:

>>> from brutalspell import BrutalSpell
>>> b = BrutalSpell('/usr/share/dict/words', True)
>>> b.check('python')
True
>>> b.check('check')
True
>>> b.check('chek')
False
>>> b.add('chek')
>>> b.check('chek')
True
>>> b.write('/tmp/b')
>>> bb = BrutalSpell('/tmp/b',0,1)
>>> bb.check('chek')
True
>>> bb.add('xyz')
>>> bb.write('/tmp/bb')
>>> bbb = BrutalSpell('/tmp/bb')
>>> bbb.check('xyz')
True
>>> bbb.add('xxyyzz')
>>> bbb.write()
>>> x = BrutalSpell('/tmp/bb')
>>> x.check('xxyyzz')
True


>>> from brutalspell import Trie
>>> t = Trie('foo')
>>> t.add('foo')
>>> t.add('spam')
>>> t.add('foobar')
>>> list(t)
[('f', 'o', 'o'), ('f', 'o', 'o', 'b', 'a', 'r'), ('s', 'p', 'a', 'm')]
>>> t.add(list(range(10)))
>>> list(t)
[('f', 'o', 'o'), ('f', 'o', 'o', 'b', 'a', 'r'), ('s', 'p', 'a', 'm'), (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)]
>>> 'foo' in t
True
>>> 'fo' in t
False
>>> t.add(list(range(5)))
>>> list(t.keys())
['f', 's', 0]
>>> list(t)
[('f', 'o', 'o'), ('f', 'o', 'o', 'b', 'a', 'r'), ('s', 'p', 'a', 'm'), (0, 1, 2, 3, 4), (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)]
>>> t.search(list(range(5)))
True
>>> t.search(list(range(7)))
False
>>> t.update('eggs spam'.split())
>>> list(t)
[('f', 'o', 'o'), ('f', 'o', 'o', 'b', 'a', 'r'), ('s', 'p', 'a', 'm'), (0, 1, 2, 3, 4), (0, 1, 2, 3, 4, 5, 6, 7, 8, 9), ('e', 'g', 'g', 's')]
>>> tuple(t)
(('f', 'o', 'o'), ('f', 'o', 'o', 'b', 'a', 'r'), ('s', 'p', 'a', 'm'), (0, 1, 2, 3, 4), (0, 1, 2, 3, 4, 5, 6, 7, 8, 9), ('e', 'g', 'g', 's'))
>>> t.tolist()
[('f', 'o', 'o'), ('f', 'o', 'o', 'b', 'a', 'r'), ('s', 'p', 'a', 'm'), (0, 1, 2, 3, 4), (0, 1, 2, 3, 4, 5, 6, 7, 8, 9), ('e', 'g', 'g', 's')]
>>> len(t)
6
>>> t[0]
<brutalspell.Trie object at 0x7ff981c3cc80>
>>> list(t[0])
[(1, 2, 3, 4), (1, 2, 3, 4, 5, 6, 7, 8, 9)]
>>> t['x']
Traceback (most recent call last):
[...]
KeyError: 'x'


>>> t = brutalspell.WTrie('foo')
>>> t.add('foobar')
>>> t.add('spam')
>>> len(t)
3
>>> list(t)
['foo', 'foobar', 'spam']
>>> 'foo' in t
True
>>> 'fo' in t
False
>>> list(t.keys())
['f', 's']
>>> list(t['f'])
['oo', 'oobar']
>>> t['x']
[...]
KeyError: 'x'
"""


"""
# removed recursive version of the add method because slower than the iterative one
# recursive version of search() is still faster

crap0101@debian:~$ python /tmp/t.py
add:    2.7539
add_it: 2.2532
t.search:    0.9787
t.search_it: 2.2759


import brutalspell
t = brutalspell.Trie()
t1 = brutalspell.Trie()
t2 = brutalspell.Trie()

def add(data):
    t = brutalspell.Trie()
    for x in data:
        t.add(x)
def add_it(data):
    t = brutalspell.Trie()
    for x in data:
        t.add_it(x) # removed

with open('/usr/share/dict/italian') as f:
    tot = list(l.strip() for l in f)
    data = random.choices(tot, k=1000)


print('add:    {:.4f}'.format(timeit.Timer('add(data)', globals=locals()).timeit(1000)))
#print('add_it: {:.4f}'.format(timeit.Timer('add_it(data)', globals=locals()).timeit(1000)))

t.update(tot)

print('t.search:    {:.4f}'.format(timeit.Timer('for x in data:t.search(x)', globals=locals()).timeit(1000)))
print('t.search_it: {:.4f}'.format(timeit.Timer('for x in data:t.search_it(x)', globals=locals()).timeit(1000)))
"""
