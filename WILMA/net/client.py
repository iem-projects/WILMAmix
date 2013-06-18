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


def client(host='', port=0, oscprefix=None, verbose=False, transport='udp', backend=None):
    if backend is None:
        backend = 'pyside'
    elif type(backend) is str:
        backend=backend.lower()
        if 'gui' == backend:
            backend='pyside'
        elif ('smi' == backend) or ('sm' == backend):
            backend='gobject'

    if backend == 'gobject':
        if 'udp' == transport:
            import clientUDP
            return clientUDP.clientUDP(host=host, port=port, oscprefix=oscprefix, verbose=verbose)
        elif 'tcp' == transport:
            import clientTCP
            return clientTCP.clientTCP(host=host, port=port, oscprefix=oscprefix, verbose=verbose)
        raise Exception("invalid stream transport: "+transport)
    elif backend == 'pyside':
        if 'udp' == transport:
            import clientUDP_PySide as clientUDP
            return clientUDP.clientUDP(host=host, port=port, oscprefix=oscprefix, verbose=verbose)
        elif 'tcp' == transport:
            import clientTCP_PySide as clientTCP
            return clientTCP.clientTCP(host=host, port=port, oscprefix=oscprefix, verbose=verbose)
        raise Exception("invalid stream transport: "+transport)

    raise Exception("invalid network backend: "+backend)




######################################################################

##if __name__ == '__main__':
##    pass
