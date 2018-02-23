#!/usr/bin/python

from itertools import combinations, permutations
from operator import mul
from math import sqrt, factorial as fact

debug = False

___doc___ = '''
kenken.py

Many methods provided to supplement human logic in solving a KenKen puzzle.

This module does not aim to solve a puzzle for you. You must still apply logic
and common sense with the results obtained here. However, with larger puzzles
(9 or more) the impossible becomes quite doable.

The most useful functions will be krange, comb, and lShapes.

krange is best used as an input for these functions. krange(n,a,b,c) may be
read as "all the numbers from 1 to n except for a, b and c". These numbers do
not need to be less than or equal to n to be used in this invocation.

comb() is used to describe the possible contents of a series of colinear boxes.
It returns sorted, nonrepeating tuples. Its contents may be filtered via addsTo
and multTo, about which more below.

lShapes() is used to describe the possible contents of any shape consisting of
line of boxes (as with comb) with exactly one box adjacent that is off that
line. The most common use is with a so-called triangle such as ".:". It may,
like comb(), be filtered via addsTo and multTo, about which more below. It also
takes a filter argument noDouble, which is a collection of numbers that may not
appear twice in the shape.

addsTo and multTo specify respectively the sum and the product of the shape you
are analyzing. Each parameter may take either a single numerical value, a list
of them, or a function that takes integer input and returns a boolean. They may
be used together, though this is rarely called for.

Example usage:

Suppose you have a 9-sized puzzle, and a pair of adjacent boxes that must add
up to 10; outside those boxes, a 1 and a 3 are present in the row.
comb(krange(9,1,3),2,addsTo=10) lists all the pairs of numbers that may
populate this pair of boxes.

>>> lShapes(9,3,multTo=72,addsTo=14)
(((2, 6), 6), ((3, 8), 3))

'''

if debug:
  def log(x): print x
else:
  def log(x): pass

kenken_proc = lambda x: x
#kenken_proc = tuple
#kenken_proc = list

def pfactors(n):
  '''lists all prime factors (with multiplicity) of the input.'''
  def inner(n):
    f = 2
    while n>1:
      q,r = divmod(n,f)
      if r==0:
        yield f
        n = q
      else:
        f += 1
  return list(inner(n))

def _filt(coll,addsTo=None,multTo=None):
  '''inner utility function'''
  log('pre-beginning filt')
  def makeFunc(crit,op):
    if crit is None: return lambda x: True
    elif hasattr(crit,'__contains__'):
      return lambda T: op(T) in crit
    elif hasattr(crit,'__call__'):
      return lambda T: crit(op(T))
    else: return lambda T: op(T)==crit
  plTest = makeFunc(addsTo,sum)
  mltTest = makeFunc(multTo,prod)
  log('begin filt loop')
  for T in coll:
    log('yield returns')
    if plTest(T) and mltTest(T):
      log('passed test '+str(T))
      yield T

def _range(_b,n,excluded):
  log('beginning _range loop')
  for x in xrange(1 if _b else 0,n+1):
    log('_range loop')
    if x not in excluded:
      log('_range yields')
      yield x

def krange(n,*excluded):
  '''krange(n,[a,[b,[c,...]]]) --> a list
    returns a sorted list of all integers from 1 to n,
    excluding a,b,c, &c if provided'''
  log('beginning krange')
  return list(_range(True,n,excluded))

def zrange(n,*excluded):
  '''zrange(n,[a,[b,[c,...]]]) --> a list
    returns a sorted list of all integers from 0 to n,
    excluding a,b,c, &c if provided'''
  log('beginning zrange')
  return list(_range(False,n,excluded))

def comb(C,n,addsTo=None,multTo=None):
  '''comb(C,n[,addsTo][,multTo]) --> iterable object of tuples
    Used to analyze possibilities for a KenKen row of length n. Provides all
    possible tuples of size n drawn from the collection C. If C is an integer,
    krange(C) is automatically substituted. Can be filtered via addsTo and
    multTo -- see module help for more information.'''
  if isinstance(C,(int,long)): C = krange(C)
  return list(_filt(combinations(C,n),addsTo=addsTo,multTo=multTo))

def lShapes(C,n,C2=None,addsTo=None,multTo=None,noDouble=()):
  '''lShapes(C,n[,C2][,addsTo][,multTo][,noDouble]) --> iterates pairs (T,t)
    Used to analyze shapes which are a row of size n-1 plus one box outside
    the row -- eg ".:" or "..:" or ".:.". Returns pairs (T,t); T is a tuple
    corresponding to the row, and t is the number in the extraneous box. Can
    be filtered via addsTo and multTo -- see module help for more. C and C2
    respectively give the collections that T and t are drawn from; if C2 is
    omitted, it is the same as C. If C is an integer, krange(C) is
    automatically substituted. A double occurs when T contains t; noDouble is
    a collection of numbers that may not be doubles.'''
  log('pre-beginning lShapes')
  def inner(C,n,C2,noDouble):
    if isinstance(C,(int,long)): C = krange(C)
    if C2 is None: C = C2 = list(C)
    else: C = list(C) ; C2 = list(C2)
    log('starting loop')
    for T in combinations(C,n-1):
      log('level 1 of loop')
      for t in C2:
        log('level 2 of loop')
        if not (t in T and t in noDouble):
          log('yield')
          yield T + (t,)
    log('ending loop')
  log('lShapes')
  for T in _filt(inner(C,n,C2,noDouble), addsTo=addsTo,multTo=multTo):
    yield T[:-1],T[-1]

def boxShapes(C,addsTo=None,multTo=None,noDouble=()):
  '''boxShapes(C[,addsTo][,multTo][,noDouble]) --> iterates over tuples
    Used to analyze boxes of 2x2. Each tuple is potential contents of a box,
    with contents drawn from C. At most one number may appear twice, unless it
    is present in the collection noDouble. May be filtered via addsTo and
    multTo -- see module help for more information.'''
  def inner(C,noD):
    for T in comb(C,4): yield T
    for d in C:
       if d not in noD:
         for x,y in comb(C,2):
           if d not in (x,y):
             if d<x: yield (d,d,x,y)
             elif d<y: yield (x,d,d,y)
             else: yield (x,y,d,d)
  if isinstance(C,(int,long)): C = krange(C)
  return _filt(inner(list(C),noDouble),addsTo=addsTo,multTo=multTo)

def prod(C):
  '''utility function -- gives the product of all numbers in C.'''
  return reduce(mul,C,1)

def prods(C): return sorted(set(map(prod,C)))
def sums(C): return sorted(set(map(sum,C)))


def lShapesSummary(C,n,C2=None,addsTo=None,multTo=None,noDouble=()):
  '''lShapesSummary(args) --> pair (T,U)
    This is used to summarize the output of lShapes. The list T contains all
    numbers that may be in the row of the L-shape; U contains all numbers that
    may be in the extraneous box of it.'''
  log('begin lShapesSummary function')
  if isinstance(C,(int,long)):
    log('making list')
    C = list(krange(C))
  sols = list(lShapes(C,n,C2,addsTo,multTo,noDouble))
  return [k for k in C if any(k in T for T,t in sols)], \
            sorted(set(t for T,t in sols))

def div(P):
  '''div(P) --> function mapping integers to booleans
    Useful mostly as a value for multTo. div(P)(x) is true if and only if
    P%x==0. For example, if you have a complicated shape with a product
    value of 150, you can try combinations for one row that is a part of it
    by specifying multTo=div(150).'''
  return lambda x: P%x==0

def atmost(P):
  '''atmost(P) --> function mapping integers to booleans
    Useful mostly as a value for addsTo. atmost(P)(x) is true if and only if
    x<=P. For example, if you have a complicated shape consisting of two rows
    of two and an extraneous box that add up to 40, one row plus the single box
    are at least 4, so the remaining row is at least 36; you can analyze it
    with addsTo=atmost(36).'''
  return lambda x: x<=P

#def maxrest(P):
