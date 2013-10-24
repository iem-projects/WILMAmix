#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright © 2013, IOhannes m zmölnig, IEM

# This file is part of WILMix
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with WILMix.  If not, see <http://www.gnu.org/licenses/>.

## tools for handling timestamps


## unwrap timestamps based on a `wrap`-value
## this whould return the "best" guess for unwrapping

def _unwrap(v, v0, w, w2):
#v=testvalue; v0=pivotpoint; w=range; w2=range/2
    if(v0-v)>w2: return (v%w)+w
    if(v-v0)>w2: return (v%w)-w
    return v

def unwrapTS(values, wrap=0xFFFFFFFF, pivot=None):
    w2=wrap/2
    if pivot is None:
        dist=None
        result=[]
        for v0 in values:
            guess=[_unwrap(x, v0, wrap, w2) for x in values]
            _dist=max(guess)-min(guess)
            if dist is None or (_dist < dist):
                dist=_dist
                result=guess
        return result

    ## simply wrap around the given pivot piont
    v0=values[pivot]
    return [_unwrap(x, v0, wrap, w2) for x in values]
    
## extract list of elements that are within a given range
def getLargestRangedSublist(values, _range, _wrap=10):
    pass

if __name__ == '__main__':
    def test_unwrap(v, v0, w):
        print("unwrap(%d,%d,%d) -> %d" % (v, v0, w, _unwrap(v, v0, w, w/2)))
    def test_unwrapTS(l, w, pivot=None):
        print("unwrapTS(%s,%s,%s) -> %s" % (l, w, pivot, unwrapTS(l, w, pivot)))

    test_unwrap(2, 1, 10)
    test_unwrap(9, 1, 10)
    test_unwrap(8, 9, 10)
    test_unwrap(1, 9, 10)
    test_unwrap(3, 9, 10)


    test_unwrapTS([1,2,3, 9], 10)

    test_unwrapTS([1,2, 6,7,8,9], 10)

    test_unwrapTS([0,1,2,3], 4, 0)
    test_unwrapTS([0,1,2,3], 4, 1)
    test_unwrapTS([0,1,2,3], 4, 2)
    test_unwrapTS([0,1,2,3], 4, 3)
    test_unwrapTS([0,1,2,3], 4)

#
#    def _testrange(l):
#        print("%s -> %s" % (l, getRangedTS(l)))


