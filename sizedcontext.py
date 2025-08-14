# Author: Marco Chieppa
# Year: 2025

# Copyright (c) 2025  Marco Chieppa | crap0101

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


from collections.abc import Callable, Sequence
import operator

class SizedQueue:
    """A simple FIFO queue storing at most *max* items."""
    def __init__ (self, max=float('+inf')):
        self._max = max
        self._items = []
        self._count = 0

    def push (self, item):
        self._items.append(item)
        if self._count == self._max:
            self._items.pop(0)
        else:
            self._count += 1
    def pop(self):
        if self._count > 0:
            self._count -= 1
        return self._items.pop()
    def items(self):
        for item in self._items:
            yield item
    def empty(self):
        self._items = []
        self._count = 0
# XXX+TODO: compare SizedQueue with collection.deque

class ContextIter:
    """
    Filters a given sequence using a callable for matching elements,
    keeping an amount of pre/post context.
    """
    def __init__ (self, seq: Sequence = [], match: Callable = operator.truth, ctx_pre=0, ctx_post=0):
        if ctx_pre < 0 or ctx_post < 0:
            raise ValueError("ctx_pre and ctx_post must be >= 0")
        self._seq = seq
        self._match = match
        self._qpre = SizedQueue(ctx_pre)
        self._ctx_pre = ctx_pre
        self._ctx_post = ctx_post
    def __str__ (self):
        return 'ContexIter({},{},{})'.format(self._match.__name__,self._ctx_pre,self._ctx_post)
    def getctx (self):
        post_ctx = 0
        for i in self._seq:
            if self._match(i):
                for p in self._qpre.items():
                    yield p
                yield i
                self._qpre.empty()
                post_ctx = self._ctx_post
            elif post_ctx:
                yield i
                post_ctx -= 1
            else:
                self._qpre.push(i)
    def getctxcall (self):
        post_ctx = 0
        for i in self._seq:
            if self._match(i):
                for p in self._qpre.items():
                    yield p
                yield i
                self._qpre.empty()
                post_ctx = self._ctx_post
            elif post_ctx:
                yield i
                post_ctx -= 1
            else:
                self._qpre.push(i)


def _example():
    lst = [0,1,False,True]
    c=ContextIter(lst, ctx_pre=0,ctx_post=0)
    print(c,lst)
    for i in c.getctx():print(i,end=', ')
    print();print('-'*20)

    lst=[0, 'x', 1, 2, 3, 4, 5, 'x',
         6, 7, 8, 9, 10, 11, 20, 'x',
         21, 22, 23, 24, 25, 26, 27, 28, 29, 'x']
    c=ContextIter(lst,lambda i:i=='x', 3,3)
    print('x',c,lst)
    for i in c.getctx():print(i,end=', ')
    print();print('-'*20)

    c=ContextIter(lst,lambda i:i=='x', 1,0)
    print('x',c,lst)
    for i in c.getctx():print(i,end=', ')
    print();print('-'*20)

    c=ContextIter(lst,lambda i:i=='x', 0,1)
    print('x',c,lst)
    for i in c.getctx():print(i,end=', ')
    print();print('-'*20)

    c=ContextIter(lst,lambda i:i=='x',0,0)
    print('x',c,lst)
    for i in c.getctx():print(i,end=', ')
    print();print('-'*20)

    lst=['x',1,2,'x',3,'x',4]
    c=ContextIter(lst,lambda i:i=='x', 3,3)
    print('x',c,lst)
    for i in c.getctx():print(i,end=', ')
    print();print('-'*20)

    c=ContextIter(lst,lambda i:i=='x', 0,0)
    print('x',c,lst)
    for i in c.getctx():print(i,end=', ')
    print();print('-'*20)

    c=ContextIter(lst,lambda i:i=='y', 2,3)
    print('y',c,lst)
    for i in c.getctx():print(i,end=', ')
    print();print('-'*20)

    c=ContextIter(lst,lambda i:i=='y', 0,0)
    print('y',c,lst)
    for i in c.getctx():print(i,end=', ')
    print();print('-'*20)

__doc__ =  '''
ContexIter(truth,0,0) [0, 1, False, True]
1, True, 
--------------------
x ContexIter(<lambda>,3,3) [0, 'x', 1, 2, 3, 4, 5, 'x', 6, 7, 8, 9, 10, 11, 20, 'x', 21, 22, 23, 24, 25, 26, 27, 28, 29, 'x']
0, x, 1, 2, 3, 4, 5, x, 6, 7, 8, 10, 11, 20, x, 21, 22, 23, 27, 28, 29, x, 
--------------------
x ContexIter(<lambda>,1,0) [0, 'x', 1, 2, 3, 4, 5, 'x', 6, 7, 8, 9, 10, 11, 20, 'x', 21, 22, 23, 24, 25, 26, 27, 28, 29, 'x']
0, x, 5, x, 20, x, 29, x, 
--------------------
x ContexIter(<lambda>,0,1) [0, 'x', 1, 2, 3, 4, 5, 'x', 6, 7, 8, 9, 10, 11, 20, 'x', 21, 22, 23, 24, 25, 26, 27, 28, 29, 'x']
x, 1, x, 6, x, 21, x, 
--------------------
x ContexIter(<lambda>,0,0) [0, 'x', 1, 2, 3, 4, 5, 'x', 6, 7, 8, 9, 10, 11, 20, 'x', 21, 22, 23, 24, 25, 26, 27, 28, 29, 'x']
x, x, x, x, 
--------------------
x ContexIter(<lambda>,3,3) ['x', 1, 2, 'x', 3, 'x', 4]
x, 1, 2, x, 3, x, 4, 
--------------------
x ContexIter(<lambda>,0,0) ['x', 1, 2, 'x', 3, 'x', 4]
x, x, x, 
--------------------
y ContexIter(<lambda>,2,3) ['x', 1, 2, 'x', 3, 'x', 4]

--------------------
y ContexIter(<lambda>,0,0) ['x', 1, 2, 'x', 3, 'x', 4]

--------------------
'''

if __name__ == '__main__':
    _example()
