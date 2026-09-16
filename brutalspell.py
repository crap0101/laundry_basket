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
        self._init_data = data_or_file if self._fromfile else None # keeps filenames only
        self._use_set = bool(use_set)
        self._data = set() if self._use_set else WTrie()
        if self._init_data:
            if self._fromfile:
                self.load(data_or_file, self._rawfile)
        elif self._init_data is not None:
            self.add(data_or_file)

    def __len__ (self) -> int:
        """Returns the number of current words."""
        return len(self._data)

    def add (self, word_or_seq: Str|Seq) -> None:
        """
        Adds *word_or_seq* to the internal set of words used for spell checking.
        If *writeonfile* is a true value, write out the updated set in the path
        indicated by the *data_or_file* argument of the __init__ UNLESS you
        provide the *otherfile* argument, which must be a filepath in which
        the write will be happen.
        If *rawfile* is True write one word per line, otherwise save the words
        in the json format.
        """
        if isinstance(word_or_seq, Str):
            self._data.add(word_or_seq)
        else:
            self._data.update(word_or_seq)

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

    def write (self,
               otherfile: Str|bool = None,
               rawfile: bool = False) -> None:
        """
        Tries to write out the updated set in the path indicated by the *data_or_file*
        argument of the __init__ (or the last one possibly passed to the load() method)
        in the actual raw or json format.
        If *data_or_file* isn't a filepath throws a BrutalSpellDataError UNLESS
        you provide the *otherfile* argument, which must be a path to a file in which
        the write will be happen, (in the json format by default, or one word per line if
        *rawfile* is a true value).
        """
        if not otherfile:
            if not self._fromfile:
                raise BrutalSpellDataError("data not loaded from file, can't write out!")
            out = self._init_data
            raw = self._rawfile
        else:
            out = otherfile
            raw = rawfile
        with open(out, 'w') as out:
            if raw:
                for word in self._data:
                    print(word,end='\n',file=out)
            else:
                json.dump(tuple(self._data), out)

    def write_as (): #XXX+TODO: raw, json, ...
        pass


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


if __name__ == "__main__":
    import argparse
    import sys

    def add_func (args):
        if not (args.source_file or args.words):
            print("Nothing to add...")
            return 1
        bc = BrutalSpell(args.dest_file, args.raw_output)
        if args.source_file:
            bc.load(args.source_file, args.raw_input)
        if args.words:
            for w in args.words:
                bc.add(w)
        bc.write()

    def check_func (args):
        is_found = ('not found', 'found')
        bc = BrutalSpell(args.input_file, args.raw_input)
        result = list((w, bc.check(w)) for w in args.words)
        found = list(wr for wr in result if wr[1])
        if args.matching:
            for w, _ in found:
                print(w)
        else:
            if args.raw_output:
                for w, r in result:
                    if not r:
                        print(w)
            else:
                for w, r in result:
                    print('{}: {}'.format(w, is_found[r]))
        return len(found) != len(args.words)

    def example_func (args): # nothing but LOL
        import ast
        with open(__file__) as f:
            c = ast.parse(f.read())
        for node in ast.walk(c):
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if t.id == '_examples':
                        print(node.value.value)
                        return
        
    def make_func (args):
        bc = BrutalSpell(args.input_file, args.raw_input)
        bc.write(args.output_file, args.raw_output)

    def test_func (args):
        import timeit
        def test_load ():
            for _ in range(args.number):
                bc = BrutalSpell(args.input_file, args.raw_input)
                del bc
        print("test_load: {:.4f}".format(timeit.Timer('test_load()', globals=locals()).timeit(1) / args.number))

    _epilog = """
EXIT STATUS:
    0 if no errors, 1 otherwise.
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=_epilog)
    subparsers = parser.add_subparsers(required=True, help='Subcommands')
    # add
    add = subparsers.add_parser('add', help='add words. See `%(prog)s %(dest)s -h` for more info.')
    add.add_argument('-i', '--input-file', dest='source_file', metavar='FILE', help='words to add taken from %(metavar)s')
    add.add_argument('-r', '--raw-input', dest='raw_input', action='store_true', help='input file is in raw format (one word per line)')
    add.add_argument('-R', '--raw', dest='raw_output', action='store_true', help='output file is in raw format (one word per line)')
    add.add_argument(dest='dest_file', metavar='DEST', help='add words to file %(metavar)s')
    add.add_argument('words', nargs='*', help='optional words to add')
    add.set_defaults(main_func=add_func)
    # check
    check = subparsers.add_parser('check', help='checks for words. See `%(prog)s %(dest)s -h` for more info.')
    check_ex = check.add_mutually_exclusive_group()
    check_ex.add_argument('-m', '--only-matching', dest='matching', action='store_true', help='prints matching words only')
    check_ex.add_argument('-R', '--raw', dest='raw_output', action='store_true', help='prints only unknown words in raw format (one word per line)')
    check.add_argument('-r', '--raw-input', dest='raw_input', action='store_true', help='input file is in raw format (one word per line)')
    check.add_argument('input_file', metavar='FILE', help='loads words from %(metavar)s')
    check.add_argument('words', nargs='+', help='words to check')
    check.set_defaults(main_func=check_func)
    # make
    make = subparsers.add_parser('make',
                                 help='''makes a dict file for subsequent usage.
                                 Default file format is json. See `%(prog)s %(dest)s -h` for more info.''')
    make.add_argument('-R', '--raw', dest='raw_output', action='store_true', help='writes output file in raw format (one word per line)')
    make.add_argument('-r', '--raw-input', dest='raw_input', action='store_true', help='input file is in raw format (one word per line)')
    make.add_argument('input_file', metavar='SOURCE_FILE', help='reads words from %(metavar)s')
    make.add_argument('output_file', metavar='OUTPUT_FILE', help='writes words to %(metavar)s')
    make.set_defaults(main_func=make_func)
    #
    # test
    test = subparsers.add_parser('test', help='run tests.')
    test.add_argument('input_file', metavar='SOURCE_FILE', help='reads words from %(metavar)s')
    test.add_argument('-n', '--number', dest='number', type=int, default=1000, metavar='N', help='runs test %(metavar)s times (default: %(default)s)')
    test.add_argument('-r', '--raw-input', dest='raw_input', action='store_true', help='input file is in raw format (one word per line)')
    test.set_defaults(main_func=test_func)
    # examples
    example = subparsers.add_parser('example', help='show some usage examples.')
    example.set_defaults(main_func=example_func)

    args = parser.parse_args()
    sys.exit(args.main_func(args))


    _examples = """EXAMPLES:

>>> from brutalspell import Trie
... 
>>> t = Trie('foo')
>>> t.add('spam')
... 
>>> t.add('foobar')
>>> list(t)
[['f', 'o', 'o'], ['f', 'o', 'o', 'b', 'a', 'r'], ['s', 'p', 'a', 'm']]
>>> len(t)
3
>>> t.add('foo')
>>> len(t)
3
>>> list(t)
[['f', 'o', 'o'], ['f', 'o', 'o', 'b', 'a', 'r'], ['s', 'p', 'a', 'm']]
>>> t.update(['eggs', 'baz'])
>>> list(t)
[['f', 'o', 'o'], ['f', 'o', 'o', 'b', 'a', 'r'], ['s', 'p', 'a', 'm'], ['e', 'g', 'g', 's'], ['b', 'a', 'z']]
>>> len(t)
5
>>> t.add(range(10))
>>> t.add(range(5))
>>> list(t)
[['f', 'o', 'o'], ['f', 'o', 'o', 'b', 'a', 'r'], ['s', 'p', 'a', 'm'], ['e', 'g', 'g', 's'], ['b', 'a', 'z'], [0, 1, 2, 3, 4], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]]
>>> range(5) in t
True
>>> range(15) in t
False
>>> range(7) in t
False
>>> range(10) in t
True
>>> for x in t:x
... 
['f', 'o', 'o']
['f', 'o', 'o', 'b', 'a', 'r']
['s', 'p', 'a', 'm']
['e', 'g', 'g', 's']
['b', 'a', 'z']
[0, 1, 2, 3, 4]
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]


>>> from brutalspell import WTrie
>>> t = WTrie('foo')
>>> t.update(['eggs', 'baz'])
>>> len(t)
3
>>> list(t)
['foo', 'eggs', 'baz']
>>> t.add('spam')
>>> for x in t:x
... 
'foo'
'eggs'
'baz'
'spam'
>>> t['f']
<brutalspell.Trie object at 0x7f28ba8f5950>
>>> t['x']
Traceback (most recent call last):
...
KeyError: 'x'
>>>
>>> list(t.keys())
['f', 'e', 'b', 's']
>>> t.add('foobar')
>>> len(t)
5
>>> list(t)
['foo', 'foobar', 'eggs', 'baz', 'spam']
>>> list(t['f'])
[['o', 'o'], ['o', 'o', 'b', 'a', 'r']]


>>> from brutalspell import BrutalSpell
>>> b = BrutalSpell('/usr/share/dict/words', True)
>>> len(b)
104334
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



crap0101@debian:~$ brutalspell.py check -r /usr/share/dict/italian casa mare montagnie 
casa: found
mare: found
montagnie: not found
crap0101@debian:~$ brutalspell.py check -rm /usr/share/dict/italian casa mare montagnie 
casa
mare
crap0101@debian:~$ brutalspell.py make -Rr /usr/share/dict/italian /tmp/ita # like cp :-D
crap0101@debian:~$ diff <(sort /usr/share/dict/italian) <(sort /tmp/ita);echo $?
0
crap0101@debian:~$ brutalspell.py make -r /usr/share/dict/italian /tmp/ita.json
crap0101@debian:~$ brutalspell.py check /tmp/ita.json casa mare montagnie 
casa: found
mare: found
montagnie: not found
crap0101@debian:~$ # or, as a module:
crap0101@debian:~$ python -m brutalspell check /tmp/ita.json casa mare montagnie 
casa: found
mare: found
montagnie: not found
crap0101@debian:~$ brutalspell.py make -R /tmp/ita.json /tmp/ita.txt # reverting
crap0101@debian:~$ diff <(sort /usr/share/dict/italian) <(sort /tmp/ita.txt);echo $?
0
crap0101@debian:~$ brutalspell.py check -r /tmp/ita.txt casa mare montagnie 
casa: found
mare: found
montagnie: not found

"""
