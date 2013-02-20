#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright © 2012, Asanka P. Sayakkara, http://recolog.blogspot.co.at
# Copyright © 2013, IOhannes m zmölnig, IEM

# This file is part of MINTmix
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
# along with MINTmix.  If not, see <http://www.gnu.org/licenses/>.


# values declared in octal
SLIP_END     = bytearray([0300])
SLIP_ESC     = bytearray([0333])
SLIP_ESC_END = bytearray([0333, 0334])
SLIP_ESC_ESC = bytearray([0333, 0335])
DEBUG_MAKER  = bytearray([0015])

class SLIP:
    def __init__(self):
        self.data=bytearray()

    def getData(self):
        return self.data

    def put(self, data):
        """append a new packet"""
        self.data+=SLIP_END
        try:
            self.data+=(data
                        .replace(SLIP_ESC, SLIP_ESC_ESC)
                        .replace(SLIP_END, SLIP_ESC_END)
                        )
        except None:
            raise
        self.data+=SLIP_END
        return self
    def __add__(self, data):
        return self.put(data)

    def append(self, data):
        """raw append some data to stream"""
        try:
            self.data+=data
        except TypeError:
            self.data.append(data)            

    def get(self):
        """
        decode packets in the data retrieved so far and return them as a list of strings.
        decoded packets are removed.
        """
        #get the data till the next SLIP_END, replace escaped characters and put them into result
        #LATER make a strict decoder, where each packet MUST start with SLIP_END
        temparray=self.data.split(SLIP_END)
        self.data=temparray.pop()
        result=[]
        for b in temparray:
            if len(b) != 0:
                result+=[str(b
                             .replace(SLIP_ESC_ESC, SLIP_ESC)
                             .replace(SLIP_ESC_END, SLIP_END)
                             )]
        return result


if __name__ == '__main__':
    def printRaw(x):
        print x," [",type(x),"]"
        if type(x) is str:
            for _x in x: print "  ",ord(_x)
        else:
            for _x in x: print "  ",_x
    s0='fugu'
    s1='bohne'
    slip=SLIP()
    slip+=s0
    slip+=s1
    print "ORG0: ", s0
    print "ORG1: ", s1
    print "SLIP: ", slip
    print "SLIP* ", slip.getData()
    for s in slip.get():
        print "GOT: ",s
    print "SLIP* ", slip.getData()

    print
    s0=''
    s1=''

    s0=str('fugu'+SLIP_END)
    s1='bohne'
    slip=SLIP()
    slip+=s0
    slip.append(SLIP_END)
    slip.append(s1)
    slip.append(SLIP_ESC)
    slip.append(SLIP_END)
    slip.append('aus')
    print "ORG0: ", s0
    printRaw(s0)
    print "ORG1: ", s1
    printRaw(s1)
    print "SLIP: ", slip
    print "SLIP* ", slip.getData()
    for s in slip.get():
        print "GOT: ",s
        printRaw(s)

    print "SLIP* ", slip.getData()
    printRaw(slip.getData())
