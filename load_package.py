
import imp
import os
import sys

def load_package_as (path, name):
    path = path.rstrip(os.path.sep)
    head, tail = os.path.split(path)
    p = imp.find_module(tail, [head])
    return imp.load_module(name, *p)


if __name__ == '__main__':
    path, name = sys.argv[1:3]
    package = load_package_as(path, name)
    print (package)
    print(dir(package))



"""
EXAMPLE

crap0101@crap0101-M:~$ ls -R /tmp/spam/
/tmp/spam/:
src

/tmp/spam/src:
__init__.py  m1.py  m2.py
crap0101@crap0101-M:~$ cat bar.py 
from spam import m2

def more_eggs():
    print "more eggs from bar"
    m2.egg()
crap0101@crap0101-M:~$ python
Python 2.7.2+ (default, Oct  4 2011, 20:06:09) 
[GCC 4.6.1] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import bar
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "bar.py", line 1, in <module>
    from spam import m2
ImportError: No module named spam
>>> 
crap0101@crap0101-M:~$ python
Python 2.7.2+ (default, Oct  4 2011, 20:06:09) 
[GCC 4.6.1] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import imp
>>> import os
>>> import sys
>>> 
>>> def load_package_as (path, name):
...     path = path.rstrip(os.path.sep)
...     head, tail = os.path.split(path)
...     p = imp.find_module(tail, [head])
...     m = imp.load_module(name, *p)
... 
>>> import spam
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ImportError: No module named spam
>>> load_package_as('/tmp/spam/src', 'spam')
>>> import spam
>>> spam
<module 'spam' from '/tmp/spam/src/__init__.py'>
>>> from spam import m1
>>> m1.spam()
spam func from m1
>>> from bar import more_eggs
>>> more_eggs()
more eggs from bar
egg func from m2
>>>

############################################################

crap0101@crap0101-M:~$ python -i load_package.py /tmp/spam/src/ eggs
<module 'eggs' from '/tmp/spam/src/__init__.pyc'>
['__builtins__', '__doc__', '__file__', '__name__', '__package__', '__path__']
>>> from eggs import m1
>>> m1.spam()
spam func from m1
>>> import eggs.m2
>>> eggs.m2.egg()
egg func from m2
>>> 

"""
