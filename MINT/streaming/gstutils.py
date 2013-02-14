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

import gst

def checkElement(element):
    """
    takes an element description (including properties in a gst-launch style
    and checks whether the element exists
    (and whether the properties are could be set in theory)
    """
    elements=element.split()
    name=elements[0]
    try:
        factory=gst.element_factory_find(name)
        if factory is None:
            return False

        e=factory.create()
        for propstring in elements[1:]:
            prop=propstring.split('=')[0]
            x=e.get_property(prop)
        del e
        del factory
    except:
        return False
    return True



######################################################################
if __name__ == '__main__':
    print gstutils.checkElement('audioconvert')
