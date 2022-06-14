import operator

class NodeError(Exception):
    pass

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
    @property
    def parent (self):
        return self._parent
    @parent.setter
    def parent (self, node):
        self._parent = node
    @property
    def value (self):
        return self._value
    @value.setter
    def value (self, value):
        self._value = value
    @property
    def childs (self):
        return tuple(self._childs)
    @childs.setter
    def childs (self, seq):
        self._childs = list(seq)
    def add_child (self, node):
        self._childs.append(node)
    def remove_child (self, node):
        self._childs.remove(node)
    def is_root (self):
        return self._parent == None

class ListNode(Node):
    def __init__(self, value=None, parent=None):
        super().__init__(value, parent)
        self.childs = (None,)
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
        raise NotImplementedError('ListNode cannot add child')
    def remove_child (self, node):
        raise NotImplementedError('ListNode cannot remove child')


class SortedList:
    def __init__ (self, seq=None):
        if seq:
            it = iter(seq)
            v = next(it)
            self._set_root(v)
            self.extend(it)
        else:
            self._set_root(None)
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






    
###############################################
class _SortedTree:
    def __init__ (self, initval=None):
        raise NotImplementedError
        self._root = self._mknode(initval)
        self._node_min = self._node_max = self._root


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
"""
