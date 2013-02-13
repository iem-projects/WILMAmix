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

import socket

class Constants:
    MINT_HOSTNAME = socket.gethostname()
    MINT_MIXER_CONTROLNUM = 4  ## FIXME '4' is hardcoded to the SMi's 'Amp' control
    if MINT_HOSTNAME == 'umlautO':
        MINT_MIXER_CONTROLNUM = 1  ## stub
    elif MINT_HOSTNAME == 'ferrari':
        MINT_MIXER_CONTROLNUM = 3  ## stub
