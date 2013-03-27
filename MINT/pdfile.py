#!/usr/bin/env python
# -*- coding: utf-8 -*-

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



################################################################
##import pyalsa.alsahcontrol as alsahcontrol
##hctl = alsahcontrol.HControl()
###hctl.list()
###element = alsahcontrol.Element(hctl,(4, 2, 0, 0, 'Amp Capture Volume', 0))
##element = alsahcontrol.Element(hctl,4)
##info = alsahcontrol.Info(element)

##value = alsahcontrol.Value(element)

##value.read()
##values = value.get_tuple(info.type, info.count)


##value.set_tuple(info.type, (10,))
##value.write()
################################################################

import re

class pdfile:
    def __init__(self, filename):
        with open(filename, 'r') as f:
            content = f.read()
        content=content.replace('\\;', '')
        content=content.replace('\n', '')
        content=content.replace('\r', '')
        self.content = content.split(';')
        self.inlets=(0,0)
        self.outlets=(0,0)
        self._parse()

    def _parse(self):
        depth=0
        re_inlet  =re.compile('^#X obj [0-9]+ [0-9]+ inlet( .*)?$')
        re_inletS =re.compile('^#X obj [0-9]+ [0-9]+ inlet~( .*)?$')
        re_outlet  =re.compile('^#X obj [0-9]+ [0-9]+ outlet( .*)?$')
        re_outletS =re.compile('^#X obj [0-9]+ [0-9]+ outlet~( .*)?$')

        n_inlet=0
        n_outlet=0
        n_inletS=0
        n_outletS=0
        for l in self.content:
            if l.startswith('#N canvas'):
                depth+=1
            elif l.startswith('#X restore'):
                depth-=1
            if depth is 1:
                if re_inlet.search(l) is not None:
                    n_inlet+=1
                elif re_inletS.search(l) is not None:
                    n_inletS+=1
                elif re_outlet.search(l) is not None:
                    n_outlet+=1
                elif re_outletS.search(l) is not None:
                    n_outletS+=1
        self.inlets=(n_inlet, n_inletS)
        self.outlets=(n_outlet, n_outletS)
        
    def getInlets(self):
        return self.inlets
    def getOutlets(self):
        return self.outlets

######################################################################

if __name__ == '__main__':
    import sys
    for arg in sys.argv[1:]:
        try:
            pd = pdfile(arg)
            inlets=pd.getInlets()
            outlets=pd.getOutlets()
            print "FILE     :", arg
            print "inlets   :", inlets[0]
            print "inlets~  :", inlets[1]
            print "outlets  :", outlets[0]
            print "outlets~ :", outlets[1]
            print ""
        except:
            print "unable to open file: ", arg



