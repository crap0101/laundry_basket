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
from typing import Union

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
    def __init__(self, word: Str = ()):
        self.subt = {}
        self.EOS = False
        if word:
            self.add(word)

    def __contains__ (self, word: Str) -> bool:
        """Returns True if *words* belongs to this trie."""
        return self.search(word)
    def __getitem__ (self, c: Str) -> Trie:
        """Returns the sub-trie associated at the *c* key."""
        return self.subt[c]
    def __setitem__ (self, c: Str, v: Trie) -> None:
        """Sets the value *v* (must be a Trie) for the *c* key."""
        self.subt[c] = v
    def __iter__ (self) -> Iterable[Str]:
        """Yields words from this Trie."""
        for k in Trie.trie_to_list(self):
            yield k
    def __len__ (self) -> int:
        """Returns the number of words of this Trie."""
        return Trie.trie_len(self)

    def add (self, word: Str) -> None:
        """Adds *word* to this Trie."""
        if not word:
            self.EOS = True
            return
        k = word[0]
        try:
            prox = self[k]
        except KeyError:
            prox = Trie()
            self[k] = prox
        prox.add(word[1:])

    def keys (self) -> Str:
        """Yields the keys of this Tries."""
        for k in self.subt:
            yield k

    def search (self, word: Str) -> bool:
        """
        Returns True if *word* is in this trie.
        """
        return Trie.trie_search(self, word)

    def tolist (self) -> list[Str]:
        """
        Returns the words of this Trie as a list.
        """
        return Trie.trie_to_list(self)

    def update (self, seq: Seq) -> None:
        """Adds the words in the *seq* sequence to this Trie."""
        for w in seq:
            self.add(w)

    @staticmethod
    def trie_len (trie: Trie) -> int:
        """Returns the len of *trie*."""
        tot = 0
        if trie.EOS:
            tot = 1
        for k in trie.keys():
            tot += Trie.trie_len(trie[k])
        return tot

    @staticmethod
    def trie_search (trie: Trie, word: Str) -> bool:
        """Returns True if *trie* contains *word*."""
        if not word:
            if trie.EOS:
                return True
            return False
        c = word[0]
        try:
            return Trie.trie_search(trie[c], word[1:])        
        except KeyError:
            return False

    @staticmethod
    def trie_to_list (trie: Trie, pw: Str = '') -> list[Str]:
        """
        Returns the words of *trie* as a list.
        *pw* is a convenience argument since this is a recursive function,
        can be leaved empty.
        """
        words = []
        if trie.EOS:
            words.append(pw)
        for k in trie.keys():
            words.extend([s for s in Trie.trie_to_list(trie[k], pw + k)])
        return words


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
>>> t.add('foobar')
>>> t.add('spam')
>>> len(t)
3
>>> list(t)
['foo', 'foobar', 'spam']
>>> for x in t:x
... 
'foo'
'foobar'
'spam'
>>> t['f']
<__main__.Trie object at 0x7fe03c9302d0>
>>> t['x']
Traceback (most recent call last):
[...]
KeyError: 'x'
>>> list(t.keys())
['f', 's']
>>> t.search('foo')
True
>>> 'foo' in t
True
>>> 'f' in t
False
>>> 'o' in t
False
>>> t.update('foobar eggs lol'.split())
>>> len(t)
5
>>> tuple(t)
('foo', 'foobar', 'spam', 'eggs', 'lol')
>>> t.add('foo')
>>> len(t)
5
>>> tuple(t)
('foo', 'foobar', 'spam', 'eggs', 'lol')
>>> t.tolist()
['foo', 'foobar', 'spam', 'eggs', 'lol']
>>> tt = Trie('uzzz')
>>> t['u'] = tt
>>> len(t)
6
>>> t.tolist()
['foo', 'foobar', 'spam', 'eggs', 'lol', 'uuzzz']
>>> list(t.keys())
['f', 's', 'e', 'l', 'u']
"""
