import operator

class TreeNodeError(Exception):
    pass

class TreeNode:
    def __init__(self, value=None, left=None, right=None):
        if value is None and not all((left is None, right is None)):
            raise TreeNodeError('Creating a node with no value and childs')
        self.value = value
        #?# if isinstance(left, TreeNode) | None
        self.left = left
        self.right = right
    def __lt__ (self, value):
        return operator.lt(self.value, value)
    def __eq__ (self, value):
        return operator.eq(self.value, value)
    def __gt__ (self, value):
        return operator.gt(self.value, value)
    def __ne__ (self, value):
        return not self__eq(value)
    def __bool__ (self):
        return not (self.value is None)

class SortedTree:
    def __init__ (self, initval=None):
        self._root = self._mknode(initval)
        self._node_min = self._node_max = self._root
    
    def _add_node (self, n):
        node = self._root
        if not node:
            self.__init__(n.value)
            return
        while True:
            if not node.left:
                node.left = TreeNode()
            left = node.left
            if not node.right:
                node.right = TreeNode()
            right = node.right
            if n == node:
                self._insert_right(node, n, left, right)
                break
            elif n < node:
                if not left:
                    node.left = n
                    n.right = node
                    if self._node_min > n: self._node_min = n
                    break
                elif n > left:
                    self._insert_left(node, n, left, right)
                    if self._node_min > left: self._node_min = left
                    break
                else:
                    node = left
            elif n > node:
                if not right:
                    node.right = n
                    n.left = node
                    if self._node_max < n: self._node_max = n
                    break
                elif n < right:
                    self._insert_right(node, n, left, right)
                    if self._node_max < right: self._node_max = right
                    break
                else:
                    node = right

    def _get_nodes (self):
        node = self._node_min
        while node:
            yield node
            node = node.right

    def _insert_left (self, node, newnode, left, right):
        node.left = newnode
        newnode.right = node
        newnode.left = left
        left.right = newnode

    def _insert_right (self, node, newnode, left, right):
        right.left = newnode
        newnode.right = right
        newnode.left = node
        node.right = newnode

    def _max (self, node=None):
        node = node or self._root
        while node.right:
            node = node.right
        return node
    
    def _min (self, node=None):
        node = node or self._root
        while node.left:
            node = node.left
        return node

    def _mknode (self, value=None):
        node = TreeNode(value)
        node.left = TreeNode()
        node.right = TreeNode()
        return node

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
        #print("mM",self._min.value,self._max.value)
        lst = []
        node = self._node_min #self._min(self._node_min)
        while node:
            lst.append(node.value)
            node = node.right
        return lst


            
###############
#### TESTS ####
###############

def _test_SortedTree():
    import timeit
    import random
    ri = random.randint
    _min, _max = -100, 100
    r = 50
    report_time = '{:15}{:.4f}'
    ulsts = [list(range(*sorted([ri(_min, _max) for _ in 'xy']))) for _ in range(100)]
    for lst in ulsts:
        t = SortedTree()
        t.extend(lst)
        if lst:
            minv, maxv = t.min(), t.max()
            assert minv == min(lst), '{} != {}'.format(minv, min(lst))
            assert maxv == max(lst), '{} != {}'.format(maxv, max(lst))
        assert t.tolist() == sorted(lst)
    print('* assert equals: OK')
    print('*** Times:')
    t = timeit.Timer('for l in ulsts: SortedTree().extend(l).tolist()',
                      'from __main__ import SortedTree', globals=locals()).timeit(r)
    print(report_time.format('SortedTree:', t/r))
    t = timeit.Timer('for l in ulsts: sorted(l)',
                    'from __main__ import SortedTree', globals=locals()).timeit(r)
    print(report_time.format('sorted (b-in)', t/r))

def _test():
    for n, v in globals().items():
        if n.startswith('_test_'):
            print('>>> running', n)
            v()
            
if __name__ == '__main__':
    import sys
    if not sys.flags.interactive:
        _test()


"""
>>> b=SortedTree()
>>> b.tolist()
[]
>>> b.extend(range(10))
<__main__.SortedTree object at 0x7f7e34d29eb0>
>>> b.tolist()
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
>>> b.extend(range(10,1,-1))
<__main__.SortedTree object at 0x7f7e34d29eb0>
>>> b.tolist()
[0, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10]
>>> b.add(7)
>>> b.add(12)
>>> b.add(-12)
>>> b.tolist()
[-12, 0, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 7, 8, 8, 9, 9, 10, 12]
>>> b=SortedTree('d')
>>> b.extend('asdfghjkl')
<__main__.SortedTree object at 0x7f7e3392b430>
>>> b.tolist()
['a', 'd', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 's']
>>> 
"""
