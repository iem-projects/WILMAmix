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


import pyalsa.alsahcontrol
import WILMA.utils

class AudioMixer:
    def __init__(self, constants):
        ctl=int(constants['/gain_control'])
        if ctl<1:
            raise Exception("alsa control number must be > 0")
        self.hctl =  pyalsa.alsahcontrol.HControl()
        self.element = pyalsa.alsahcontrol.Element(self.hctl, ctl)
        self.info = pyalsa.alsahcontrol.Info(self.element)
        self.value = pyalsa.alsahcontrol.Value(self.element)

    def gain(self, value=None):
        if value is not None:
            if type(value) is not list:
                value=[float(value)]*self.info.count
            elif 1 is len(value):
                v=float(value[0])
                value=[v]*self.info.count
            value=[WILMA.utils.SCALE(v, 0, 1, self.info.min, self.info.max, True) for v in value]
            self.value.set_array(self.info.type, value)
            self.value.write()
        self.value.read()
        gains = self.value.get_array(self.info.type, self.info.count)
        try:
            gainsi = [WILMA.utils.SCALE(i, self.info.min, self.info.max, 0., 1., True) for i in gains]
        except TypeError: ## never try to catch _all_ errors
            print "caught TypeError (try adjusting 'SMi/gain control/' in WILMix.conf)"
            print "\tOUCH: ", gains
            print "\tmixer: ", self.info.name
            gainsi=[0]
        return  gainsi


######################################################################

if __name__ == '__main__':
    print "SM..."
    sm = WILMAsm()
    import time

    main_loop = gobject.MainLoop()
    print "start loop"
    try:
        main_loop.run()
    except KeyboardInterrupt:
        pass


