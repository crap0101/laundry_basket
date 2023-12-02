#
# author: Marco Chieppa | crap0101
#

""" Implementation of the Markov algorithm
Cfr.:
  http://en.wikipedia.org/wiki/Markov_algorithm
  http://rosettacode.org/wiki/Execute_a_Markov_algorithm
  http://web.cecs.pdx.edu/~sheard/course/CS311/Spring2011/notes/OtherTuringComputAlg.pdf
"""

import re

def markov (input, rules):
    escape = re.escape
    run = 1
    while run:
        for old, new in rules:
            input, n = re.subn(escape(old), new, input, count=1)
            if new.startswith('.'):
                run = 0
                break
            if n == 1:
                break
        else:
            break
    return input

def test ():
    rules = (
    ("A", "apple"),
    ("B", "bag"),
    ("S", "shop"),
    ("T", "the"),
    ("the shop", "my brother"),
    ("a never used", ".terminating rule"))
    input = "I bought a B of As from T S."
    print markov(input, rules)
    rules = (
    ("|0", "0||"),
    ("1", "0|"),
    ("0", ""))
    input = '101'
    print markov(input, rules)
    rules = (
        ("A", "apple"),
        ("WWWW", "with"),
        ("Bgage", "->.*"),
        ("B", "bag"),
        ("->.*", "money"),
        ("W", "WW"),
        ("S", ".shop"),
        ("T", "the"),
        ("the shop", "my brother"),
        ("a never used", ".terminating rule"))
    input = 'I bought a B of As W my Bgage from T S.'
    print markov(input, rules)
    # http://rosettacode.org/wiki/Execute_a_Markov_algorithm#Ruleset_5
    rules = (
        ("A0",  "1B"),
        ("0A1", "C01"),
        ("1A1", "C11"),
        ("0B0", "A01"),
        ("1B0", "A11"),
        ("B1",  "1B"),
        ("0C0", "B01"),
        ("1C0", "B11"),
        ("0C1", "H01"),
        ("1C1", "H11"))
    input = '000000A000000'
    print markov(input, rules)


if __name__ == '__main__':
    test()
