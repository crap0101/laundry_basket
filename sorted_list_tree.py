#
# author: Marco Chieppa | crap0101
#

"""
Implementation of some sorted collections.
 
>>> print(sys.version)
3.8.10 (default, Mar 15 2022, 12:22:08) 
[GCC 9.4.0]
"""


from collections import deque
import heapq
import operator


########
# MISC #
########

class NodeError(Exception):
    pass


################
# NODE OBJECTS #
################

class Node:
    """Base Node Object."""
    def __init__(self, value=None, parent=None):
        self._value = value
        self._parent = parent
        self._childs = []
    def __lt__ (self, value):
        return operator.lt(self.value, value)
    def __le__ (self, value):
        return operator.le(self.value, value)
    def __eq__ (self, value):
        return operator.eq(self.value, value)
    def __gt__ (self, value):
        return operator.gt(self.value, value)
    def __ge__ (self, value):
        return operator.ge(self.value, value)
    def __ne__ (self, value):
        return not (self.value == value)
    def __bool__ (self):
        return not (self.value is None)
    def __repr__ (self):
        return f'{self.__class__.__name__}({self.value})'
    def add_child (self, node):
        self._childs.append(node)
    @property
    def childs (self):
        return tuple(self._childs)
    @childs.setter
    def childs (self, seq):
        self._childs = list(seq)
    def is_leaf (self):
        return not self.childs
    def is_root (self):
        return self._parent == None
    @property
    def parent (self):
        return self._parent
    @parent.setter
    def parent (self, node):
        self._parent = node
    def remove_child (self, node):
        self._childs.remove(node)
    @property
    def value (self):
        return self._value
    @value.setter
    def value (self, value):
        self._value = value


class ListNode(Node):
    """A Node object for linked lists."""
    def __init__(self, value=None, parent=None):
        super().__init__(value, parent)
        self.childs = [None]
    @property
    def next (self):
        return self._childs[0]
    @next.setter
    def next (self, node):
        self._childs[0] = node
    @property
    def prev (self):
        return self._parent
    @prev.setter
    def prev (self, node):
        self._parent = node
    def add_child (self, node):
        raise NodeError('ListNode cannot add child')
    def remove_child (self, node):
        raise NodeError('ListNode cannot remove child')


class BinaryNode (Node):
    """A Node object with only two children.
    By convention, the left child is lesser than the right child."""
    def __init__ (self, value, parent=None):
        super().__init__(value, parent)
    def add_child (self, node):
        if len(self.childs) == 2:
            raise NodeError('BinaryNode already has two childs')
        node.parent = self
        if len(self.childs) == 1:
            if self.childs[0] > node:
                self._childs.insert(0, node)
            else:
                super().add_child(node)
    @property
    def left (self):
        return self.childs[0]
    @left.setter
    def left (self, node):
        self._childs[0] = node
    @property
    def right (self):
        return self.childs[1]
    @right.setter
    def right (self, node):
        self._childs[1] = node


###############
# SORTED TREE #
###############

class SortedTree:
    """Unbalanced sorted tree."""
    def __init__ (self, seq=None):
        if seq:
            it = iter(seq)
            v = next(it)
            self._set_root(v)
            self.extend(it)
        else:
            self._set_root(None)
    def __repr__ (self):
        return 'SortedTree(root={})'.format(self._root)

    def _add_node (self, newnode):
        if not self._root:
            self._set_root(newnode)
            return
        node = self._root
        while node:
            if newnode == node:
                self._insert_left(node, newnode)
                break
            elif newnode < node:
                if not node.left:
                    self._insert_left(node, newnode)
                    break
                else:
                    node = node.left
            elif newnode > node:
                if not node.right:
                    self._insert_right(node, newnode)
                    break
                else:
                    node = node.right

    def _insert_left (self, node, newnode):
        newnode.left = node.left
        newnode.left.parent = newnode
        newnode.parent = node
        node.left = newnode

    def _insert_right (self, node, newnode):
        newnode.right = node.right
        newnode.right.parent = newnode
        newnode.parent = node
        node.right = newnode

    def _mknode (self, value):
        node = BinaryNode(value)
        node.childs = [BinaryNode(None), BinaryNode(None)]
        return node

    def _node_ffw_left(self, node):
        while node.left:
            node = node.left
        return node

    def _node_rew (self, node):
        stack = deque()
        while node.parent:
            stack.appendleft(node.value)
            if node.right:
                node.right.parent = None
                stack.appendleft(node.right)
            node = node.parent
        stack.appendleft(node.value)
        if node.right:
            node.right.parent = None
            stack.appendleft(node.right)
        return stack

    def _set_root (self, val):
        if isinstance(val, BinaryNode):
            self._root = val
        else:
            self._root = self._mknode(val)

    def add (self, value):
        self._add_node(self._mknode(value))

    def extend (self, seq):
        for item in seq:
            self.add(item)
        return self

    def tolist(self):
        stack = deque([self._root])
        _sorted = []
        while stack:
            item = stack.popleft()
            if isinstance(item, Node):
                node = self._node_ffw_left(item)
                s = self._node_rew(node)
                stack.extendleft(s)
            else:
                _sorted.append(item)
        return _sorted


###############
# SORTED LIST #
###############

class SortedList:
    """Sorted linked list."""
    def __init__ (self, seq=None):
        if seq:
            it = iter(seq)
            v = next(it)
            self._set_root(v)
            self.extend(it)
        else:
            self._set_root(None)
    def __repr__ (self):
        return 'SortedList({},{})'.format(self._node_min,self._node_max)

    def _set_root (self, val):
        if isinstance(val, ListNode):
            self._node_min = self._node_max = self._root = val
        else:
            self._node_min = self._node_max = self._root = self._mknode(val)

    def _mknode (self, value):
        return ListNode(value)

    def _add_node (self, newnode):
        node = self._root
        if not self._root:
            self._set_root(newnode)
            return
        while True:
            if newnode <= node:
                if not node.prev:
                    node.prev = newnode
                    newnode.next = node
                    self._node_min = newnode
                    break
                elif newnode > node.prev:
                    self._insert_prev(newnode, node)
                    if newnode < self._node_min:
                        self._node_min = newnode
                    break
                else:
                    node = node.prev                    
            elif newnode > node:
                if not node.next:
                    node.next = newnode
                    newnode.prev = node
                    self._node_max = newnode
                    break
                elif newnode < node.next:
                    self._insert_next(newnode, node)
                    if newnode > self._node_max:
                        self._node_max = newnode
                    break
                else:
                    node = node.next

    def _insert_prev (self, newnode, node):
        nprev = node.prev
        nprev.next = newnode
        newnode.prev = nprev
        newnode.next = node
        node.prev = newnode

    def _insert_next (self, newnode, node):
        nnext = node.next
        nnext.prev = newnode
        newnode.next = nnext
        newnode.prev = node
        node.next = newnode

    def add (self, value):
        self._add_node(self._mknode(value))

    def extend (self, seq):
        for item in seq:
            self.add(item)
        return self

    def min (self):
        return self._node_min.value

    def max (self):
        return self._node_max.value

    def tolist (self):
        lst = []
        node = self._node_min
        while node:
            lst.append(node.value)
            node = node.next
        return lst


## Following OrderedList snze SizedOrderedList are even slower
## than SortedList, keeped here for some reasons.

class FreezeNode:
    """
    >>> import time
    >>> def foo(x):return x,time.time()
    ...
    >>> n=FreezeNode(8,foo)
    >>> n.value
    (8, 1757207818.8918788)
    >>> n.value
    (8, 1757207820.6267035)
    >>> n.value
    (8, 1757207822.1968768)
    >>> n=FreezeNode(8,foo,True)
    >>> n.value
    (8, 1757207830.1968722)
    >>> n.value
    (8, 1757207830.1968722)
    >>> n.value
    (8, 1757207830.1968722)
    >>>
    """
    def __init__ (self, value, keyfunc=None, freeze=False):
        self._value = value
        self.next = None
        self.prev = None
        self._freeze_value = None
        if keyfunc is None:
            def g():
                return self._value
        else:
            if freeze:
                self._freeze_value = keyfunc(value)
                def g():
                    return self._freeze_value
            else:
                def g():
                    return keyfunc(self._value)
        self._get_value = g

    @property
    def value (self):
        return self._get_value()


class FailedPush:
    pass


class OrderedList:
    """Linked list"""
    START = 'start'
    END = 'end'
    def __init__ (self, seq=[], keyfunc=lambda x:x, freeze=True):
        """
        Make a OrderedList from $seq.
        $keyfunc is a callable (which accept one arg, default to the identity function)
        to be applied on every element of $seq to extract the value that will be stored
        in the list as a FreezeNode.
        If $freeze is True (the default) $keyfunc is applied only the first time. If False,
        will be applied at every request for the FreezeNode's value.        
        """
        self._keyfunc = keyfunc
        self._freeze = freeze
        self._root = self._last = self._inode = None
        for v in seq:
            self.push(v)

    def __iter__ (self):
        return self

    def __next__ (self):
        if self._inode is None:
            self.reboot()
            raise StopIteration
        value = self._inode.value
        self._inode = self._inode.next
        return value

    def _init (self, value):
        """Private method: setup the root FreezeNode and other internal variables."""
        self._root = FreezeNode(value, self._keyfunc, self._freeze)
        self._inode = self._last = self._root

    def _cut_at_end (self):
        """Private method: remove and return the last element of the list."""
        if self._last is None:
            raise IndexError("pop from empty seq")
        lastval = self._last.value
        if self._last.prev is None:
            self._root = self._last = self._inode = None
        else:
            newlast = self._last.prev
            newlast.next = None
            self._last = newlast
        return lastval

    def _cut_at_start (self):
        """Private method: remove and return the first element of the list."""
        if self._root is None:
            raise IndexError("pop from empty seq")
        startval = self._root.value
        if self._root.next is None:
            self._root = self._last = self._inode = None
        else:
            newroot = self._root.next
            newroot.prev = None
            self._root = self._inode = newroot
        return startval

    def extend (self, seq):
        """Extend the list with the items from $seq."""
        for item in seq:
            self.push(item)
        return self

    def pop (self):
        """Remove and return the last element of the list."""
        return self._cut_at_end()

    def popleft (self):
        """Remove and return the first element of the list."""
        return self._cut_at_start()

    def push (self, value):
        """push and return the pushed value"""
        if self._root is None:
            self._init(value)
            return value #self._root.value
        node = self._root
        n = FreezeNode(value, self._keyfunc, self._freeze)
        while node:
            if n.value <= node.value:
                if node.prev is None:
                    node.prev = n
                    n.next = node
                    self._root = self._inode = n
                    return value #self._root.value
                    #break
                elif n.value >= node.prev.value:
                    before = node.prev
                    after = node
                    n.prev = before
                    before.next = n
                    n.next = after
                    after.prev = n
                    self._root = self._inode = before
                    return value # n.value
                    #break
                else:
                    node = node.prev
            elif n.value >= node.value:
                if node.next is None:
                    node.next = n
                    n.prev = node
                    self._last = n
                    return value
                    #break
                elif n.value <= node.next.value:
                    before = node
                    after = node.next
                    n.prev = before
                    n.next = after
                    before.next = n
                    after.prev = n
                    #self._last = after
                    return value
                    #break
                else:
                    node = node.next
            else:
                raise RuntimeError("NOOOOOOOOOOOOOOOOOOO")
        raise RuntimeError("NO PUSH")

    # push() alias:
    add = push

    def reboot(self):
        """
        Make the iterator pointer point to the first element
        of the list. For subsequent iterations.
        """
        self._inode = self._root

    def tolist (self):
        return list(self)


class SizedOrderedList(OrderedList):
    """Sized linked list"""
    START = 'start'
    END = 'end'
    def __init__ (self, maxsize, seq=[],
                  keyfunc=lambda x:x, freeze=True, cut=END):
        """
        Make a SizedOrderedList from $seq.
        Compared to OrderedList, the $maxsize argument fix the maximum size for this
        list, while $cut must be either SizedOrderedList.END (the default) or SizedOrderedList.START
        that affects the pushing in this list of subsequent values after the list is full:
        see the docstring of the push() method for details.
        """

        self._maxsize = maxsize
        self._size = 0
        if cut == self.END:
            self._sized = self._cut_at_end
        elif cut == self.START:
            self._sized = self._cut_at_start
        else:
            raise ValueError("wrong value for 'cut'")
        super().__init__(seq, keyfunc, freeze)

    @property
    def size (self):
        """Actual size"""
        return self._size

    @property
    def is_full (self):
        """True if the actual size is the max size for this list"""
        return self._size == self._maxsize

    def pop (self):
        """Remove and return the last element"""
        v = super().pop()
        self._size -= 1
        return v

    def popleft (self):
        """Remove and return the first element"""
        v = super().popleft()
        self._size -= 1
        return v

    def push (self, value):
        """Return the pushed $value or FailedPush.
        When the list is full, if cut=OrderedList.END pushing values equals or greater
        the max value in the list causes them to not be pushed and got FailedPush
        as the return value. Same when cut=OrderedList.START and the value being
        pushed is equal or lesser the min value in the list."""
        value = super().push(value)
        self._size += 1
        if self._size > self._maxsize:
            removed = self._sized()
            self._size -= 1
            #return FailedPush
            return FailedPush if removed == value else value
        return value


# For comparing SizedOrderedList's N-min and N-max values extraction:
class SizedOrderedHeap:
    """Sized linked heap"""
    MIN = 'min'
    MAX = 'max'
    def __init__ (self, maxsize, seq=[], which=MIN):
        """
        Make a SizedOrderedHeap from $seq.
        The $maxsize argument is the number of elements returned from the heap,
        while $which must be either SizedOrderedHeap.MIN (the default) or SizedOrderedHeap.MAX
        and affects which ($maxsize) values will be returned.
        """
        self._getval = self._choose_which(which)
        self._maxsize = maxsize
        self._seq = list(seq) # to mimic SizedOrderedList, no inplace use
        heapq.heapify(self._seq)

    def _choose_which (self, which):
        if which == SizedOrderedHeap.MIN:
            return heapq.nsmallest
        elif which == SizedOrderedHeap.MAX:
            return lambda n, seq: list(reversed(heapq.nlargest(n, seq)))
        else:
            raise ValueError('wrong value for "which"')

    def extend (self, seq):
        """Extend the heap with the items from $seq."""
        for item in seq:
            heapq.heappush(self._seq, item)
        return self

    def push (self, value):
        heapq.heappush(self._seq, value)

    # push alias:
    add = push

    def tolist (self, size=None, min_or_max=None):
        """
        $size and $min_or_max (both default to None) can be used to
        overload the default $maxsize and $which values for this instance.
        """
        getval = self._getval if min_or_max is None else self._set_which(min_or_max)
        getsize = self._maxsize if size is None else size
        return getval(getsize, self._seq)


###############
#### TESTS ####
###############

def _make_seqs (vmin=-10000, vmax=10000, lenght=500, numbers=20):
    import random
    r = random.randint
    seqs = list(list(r(vmin, vmax) for _ in range(lenght)) for _ in range(numbers))
    s_seqs = list(list(sorted(s)) for s in seqs)
    r_seqs = list(list(reversed(s)) for s in s_seqs)
    return seqs, s_seqs, r_seqs

def _test_eq (obj):
    """obj is the object to test, e.g. SortedList or SortedTree."""
    import itertools
    seqs, sorted_s, rev_s = _make_seqs()
    maxitems = max(map(len, itertools.chain(*(seqs, sorted_s, rev_s))))
    for rand_seq, sort_seq in zip(seqs, sorted_s):
        if obj in (SizedOrderedList, SizedOrderedHeap):
            s1 = obj(maxitems)
        else:
            s1 = obj()
        s1.extend(rand_seq)
        if obj in (SizedOrderedList, SizedOrderedHeap):
            s2 = obj(maxitems, rand_seq)
        else:
            s2 = obj(rand_seq)
        pivot = int(len(rand_seq)/2)
        if obj in (SizedOrderedList, SizedOrderedHeap):
            s3 = obj(maxitems, rand_seq[:pivot])
        else:
            s3 = obj(rand_seq[:pivot])
        for item in rand_seq[pivot:]:
            s3.add(item)
        assert s1.tolist() == s2.tolist(), f'[FAIL] s1 != s2 [{s1}]'
        assert s2.tolist() == s3.tolist(), f'[FAIL] s2 != s3 [{s2}]'
        assert s3.tolist() == sort_seq, f'[FAIL] s3 != sorted(list) [{s3}]'

def _test_heap_eq ():
    from random import randint, shuffle
    for _ in range(50):
        seq = [randint(-10000,10000) for _ in range(randint(1000,10000))]
        shuffle(seq)
        maxsize = randint(10,300)
        sl = SizedOrderedList(maxsize, seq) # cut at end
        sh = SizedOrderedHeap(maxsize, seq) # min values
        tol = sl.tolist()
        toh = sh.tolist()
        assert tol == toh, f'[MIN] tol != toh {tol}\n\n\n{toh}'
        sl = SizedOrderedList(maxsize, seq, cut=SizedOrderedList.START)
        sh = SizedOrderedHeap(maxsize, seq, which=SizedOrderedHeap.MAX)
        tol = sl.tolist()
        toh = sh.tolist()
        assert tol == toh, f'[MAX] tol != toh {tol}\n\n\n{toh}'

def _test_time (repeat=50):
    import timeit
    import itertools
    class Sorted:
        """Monkey patch for sorted()."""
        def __init__ (self, seq):
            self.seq = seq
        def tolist (self):
            return sorted(self.seq)
    seqs, sorted_s, rev_s = _make_seqs()
    maxitems = max(map(len, itertools.chain(*(seqs, sorted_s, rev_s))))
    report  = '{:30} {:.6f}s'
    mf_setup = 'from __main__ import SortedList, SortedTree, OrderedList, SizedOrderedList, SizedOrderedHeap'
    mf_stmt = '''
if {cls} in (SizedOrderedList, SizedOrderedHeap):
    for s in seqs:
        {cls}(maxitems, s).tolist()
else:
    for s in seqs:
        {cls}(s).tolist()'''
    for cls_name in 'SortedList SortedTree Sorted OrderedList SizedOrderedList SizedOrderedHeap'.split():
        t  = timeit.Timer(stmt=mf_stmt.format(cls=cls_name),
                          setup=mf_setup,
                          globals=locals()).timeit(repeat)
        print(report.format(f'{cls_name}:', t/repeat))
        
def _test():
    for cls in (SortedList, SortedTree, OrderedList, SizedOrderedList, SizedOrderedHeap):
        print('*** Test equality ({}): '.format(cls.__name__), end='')
        _test_eq(cls)
        print('OK')
    print('*** Test eq (SizedOrderedList vs SizedOrderedHeap): ', end='')
    _test_heap_eq()
    print('OK')


if __name__ == '__main__':
    import sys
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('-t', '--test', dest='test', action='store_true', help='run tests')
    p.add_argument('-T', '--times', dest='times', action='store_true', help='run times comparison')
    args = p.parse_args()
    if args.test:
        _test()
    if args.times:
        print('*** Test times')
        _test_time()

    



"""
>>> SortedList(range(10,0,-1)).tolist() == list(sorted(range(10,0,-1)))
True
>>> s = SortedList((7,6,5,4))
>>> s.tolist()
[4, 5, 6, 7]
>>> s.add(6)
>>> s.tolist()
[4, 5, 6, 6, 7]
>>> s.extend((6,7,8,-1))
<__main__.SortedList object at 0x7fc3d38ad310>
>>> s.tolist()
[-1, 4, 5, 6, 6, 6, 7, 7, 8]
>>> 
>>> s = SortedTree([11,11,5,3,8,4,5,4,7,11])
>>> s.tolist()
[3, 4, 4, 5, 5, 7, 8, 11, 11, 11]
>>> SortedTree(range(10,0,-1)).tolist() == list(sorted(range(10,0,-1)))
True
>>> s.add(1)
>>> s.add(-1)
>>> s.add(0)
>>> s.add(20)
>>> s.add(200)
>>> s.add(100)
>>> s.extend((10,30,118))
<__main__.SortedTree object at 0x7f97e8db6730>
>>> s.tolist()
[-1, 0, 1, 3, 4, 4, 5, 5, 7, 8, 10, 11, 11, 11, 20, 30, 100, 118, 200]
"""

"""
$ python sorted_list_tree.py  -tT
*** Test equality (SortedList): OK
*** Test equality (SortedTree): OK
*** Test equality (OrderedList): OK
*** Test equality (SizedOrderedList): OK
*** Test equality (SizedOrderedHeap): OK
*** Test eq (SizedOrderedList vs SizedOrderedHeap): OK
*** Test times
SortedList:                    0.371192s
SortedTree:                    0.070789s
Sorted:                        0.000475s
OrderedList:                   0.450305s
SizedOrderedList:              0.457118s
SizedOrderedHeap:              0.000623s
"""
