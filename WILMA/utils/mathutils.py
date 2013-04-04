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

def CLAMP(x, lo=0.0, hi=1.0):
    if(x<lo):
        return lo
    elif(x>hi):
        return hi
    return x

def SCALE(x, minIn, maxIn, minOut=0., maxOut=1., clamp=False):
    """scale a value from between minIn..maxIn to minOut..maxOut"""
    x=float(x)
    y=(x-minIn)*float(minOut-maxOut)/float(minIn-maxIn)+minOut
    if clamp:
        y=CLAMP(y, minOut, maxOut)
    return y

