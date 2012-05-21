#!/usr/bin/env python

# Copyright (C) 2012  Marco Chieppa (aka crap0101)

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

# Cfr: http://www.python-it.org/forum/index.php?topic=6418.0


import re
import math

_h2n_reg = re.compile('^(\d+|\d+\.\d+)\s*([a-zA-Z]+)$')

SYMBOLS = {'c': ('B', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y'),
           'c_ext': ('byte', 'kilo', 'mega', 'giga',
                     'tera', 'peta', 'exa', 'zetta', 'iotta'),
           'i': ('Bi', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi', 'Yi'),
           'i_ext': ('byte', 'kibi', 'mebi', 'gibi', 'tebi',
                     'pebi', 'exbi', 'zebi', 'yobi')
}

EXP = [i for i, _ in enumerate(SYMBOLS['c'])]
BASE = 1024

#def bytes2human (n, unit='c', format='%(value).1f %(symbol)s'):
def b2h (n, unit='c', format='%(value).1f %(symbol)s'):
    if unit not in SYMBOLS:
        raise TypeError ('unknown unit: %s' % unit)
    n = int(n)
    if n < 0:
        raise ValueError ("%d < 0" % n)
    p = int(math.log(n, BASE)) if n >= 1 else 0
    if p not in EXP:
        p = max(EXP)
    n /= float(BASE)**p
    return format % dict(value=n, symbol=SYMBOLS[unit][p])


#def human2bytes (s):
def h2b (s):
    try:
        sv, symbol = _h2n_reg.match(s).groups()
    except AttributeError:
        raise ValueError ("can't interpret %s" % s)
    if symbol == 'k':
        symbol = 'K'
    for p, symbols in enumerate(zip(*SYMBOLS.values())):
        if symbol in symbols:
            return int(float(sv) * (BASE**p))
    else:
        raise ValueError ("unknown unit: %s" % symbol)



