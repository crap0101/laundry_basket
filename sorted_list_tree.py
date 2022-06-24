"""
Implementation of some sorted collections.
 
>>> print(sys.version)
3.8.10 (default, Mar 15 2022, 12:22:08) 
[GCC 9.4.0]
"""


from collections import deque
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


###############
#### TESTS ####
###############

def _make_seqs (vmin=-10000, vmax=10000, lenght=500, numbers=20):
    import random
    r = random.randint
    seqs = [list(r(vmin, vmax) for _ in range(lenght)) for _ in range(numbers)]
    s_seqs = [list(sorted(s)) for s in seqs]
    r_seqs = [list(reversed(s)) for s in s_seqs]
    return seqs, s_seqs, r_seqs

def _test_eq (obj):
    """obj is the object to test, e.g. SortedList or SortedTree."""
    seqs, sorted_s, rev_s = _make_seqs()
    for rand_seq, sort_seq in zip(seqs, sorted_s):
        s1 = obj()
        s1.extend(rand_seq)
        s2 = obj(rand_seq)
        pivot = int(len(rand_seq)/2)
        s3 = obj(rand_seq[:pivot])
        for item in rand_seq[pivot:]:
            s3.add(item)
        assert s1.tolist() == s2.tolist(), f'[FAIL] s1 != s2'
        assert s2.tolist() == s3.tolist(), f'[FAIL] s2 != s3'
        assert s3.tolist() == sort_seq, f'[FAIL] s3 != sorted(list)'

def _test_time (repeat=50):
    import timeit
    class Sorted:
        """Monkey patch for sorted()."""
        def __init__ (self, seq):
            self.seq = seq
        def tolist (self):
            return sorted(self.seq)
    seqs, sorted_s, rev_s = _make_seqs()
    report  = '{:30} {:.6f}s'
    mf_setup = 'from __main__ import SortedList, SortedTree'
    mf_stmt = 'for s in seqs: {}(s).tolist()'
    for cls_name in 'SortedList SortedTree Sorted'.split():
        t  = timeit.Timer(stmt=mf_stmt.format(cls_name),
                          setup=mf_setup,
                          globals=locals()).timeit(repeat)
        print(report.format(f'{cls_name}:', t/repeat))
        
def _test():
    for cls in (SortedList, SortedTree):
        print('*** Test equality ({}): '.format(cls.__name__), end='')
        _test_eq(cls)
        print('OK')
    print('***Test times')
    _test_time()

if __name__ == '__main__':
    import sys
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('-t', '--test', dest='test', action='store_true', help='run tests')
    args = p.parse_args()
    if args.test:
        _test()

    



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

"""crap0101@orange:~/test$ python3 sorted_list_tree.py -t
*** Test equality (SortedList): OK
*** Test equality (SortedTree): OK
***Test times
SortedList:                    1.976663s
SortedTree:                    0.388248s
Sorted:                        0.001089s
"""
