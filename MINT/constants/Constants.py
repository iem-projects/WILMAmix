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
import ConfigParser, os
_config = ConfigParser.ConfigParser()
## if a value is in multiple files, the last file gets it
print "read config from",_config.read(['MINTmix.conf',
                                       os.path.join(os.path.dirname(os.path.abspath(__file__)), 'MINTmix.conf'),
                                       os.path.expanduser('~/.config/iem.at/MINTmix.conf'),
                                       ])

def _configGetInt(config, section, option, varname):
    if _config.has_section(section):
        try: globals()[varname] = _config.getint(section, option);
        except ConfigParser.NoOptionError:
            pass
        except ValueError:
            pass

def _configGetString(config, section, option, varname):
    if _config.has_section(section):
        try: globals()[varname] = _config.get(section, option);
        except ConfigParser.NoOptionError:
            pass
        except ValueError:
            pass

####################################################
# default values

HOSTNAME = socket.gethostname()
MIXER_CONTROLNUM = 4

SM_PORT=7777 # LATER change to 0

PROTOCOL='udp'
SERVICE ='_mint-sm'

# override values via config files
_configGetString(_config, 'General', 'ID', 'HOSTNAME')
_configGetString(_config, 'General', 'proto', 'PROTOCOL')
_configGetInt(_config, 'SMi', 'gain control', 'MIXER_CONTROLNUM')
_configGetInt(_config, 'SMi', 'port', 'SM_PORT')

#
####################################################
