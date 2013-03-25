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
import ast as _ast

### OSC-style configuration
# mapping ConfigParser to a diectionary of OSC-addresses
# e.g.
##  [DEFAULTS] # common for both MIXer and SMi
##  /id=blurb
##  /indir=/tmp/default
##  [MIX] # MIXer configuration (inherits from [DEFAULTS])
##  /outdir=/tmp/pull
##  /indir=/tmp/push
##  [SM]  # generic SMi config (inherits from [DEFAULTS]
##  /outdir=/tmp/sm/bla
##  [blurb] # special SMi config for ID 'blurb' (inherits from [SM] and [DEFAULTS])
##  /outdir=/tmp/blu
##  [blarb] # special SMi config for ID 'blarb' (inherits from [SM] and [DEFAULTS])
##  /id=fugel # ID here is ignored
# results in
##  mix['/id'    ]="blurb"
##  mix['/outdir']="/tmp/pull"
##  mix['/indir' ]="/tmp/push"
##  SM ['/id'    ]="blurb"
##  SM ['/outdir']="/tmp/blu"
##  SM ['/indir' ]="/tmp/default"

def _getDict(config, section):
    d=dict()
    if not config.has_section(section):
        config.add_section(section)
    for o in config.options(section):
        v=config.get(section, o)
        d[o]=v
    return d

def _setDict(config, section, values):
    id=values['/id']
    if not config.has_section(section):
        config.add_section(section)
    config.set(section, '/id', id)
    for o in values.keys():
        if o is not '/id':
            config.set(section, o, values[o])
        
## DEFAULT values
# use STRING type for everything (even for numbers)
# they will be converted to numbers automatically in the _getDict() functions
_defaults=dict()
_defaults['/id'      ] = socket.gethostname()

try:
    import getpass
    _defaults['/user']=getpass.getuser()
except ImportError:
    _defaults['/user']='unknown'

_defaults['/protocol'] = 'udp'
_defaults['/service' ] = '_mint-sm'
_defaults['/port'    ] = '7777' # LATER change to 0
_defaults['/gain_control'] = '4' ## alsa control for mic amp

_defaults['/path/in' ] = '/tmp/MINT/in'
_defaults['/path/out'] = '/tmp/MINT/out'

_defaults['/stream/type'    ]='rtp' # const
_defaults['/stream/channels']='4' # const
_defaults['/stream/profile' ]='L16' # const for now


_config = ConfigParser.ConfigParser(_defaults)
_config.read(['MINTmix.conf',
              os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'MINTmix.conf'),
              os.path.expanduser('~/.config/iem.at/MINTmix.conf'),
              ])
_mixConf=_getDict(_config, 'MIX')

_smDefaults=_getDict(_config, 'SM')
_config = ConfigParser.ConfigParser(_smDefaults)
_config.read(['MINTmix.conf',
              os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'MINTmix.conf'),
              os.path.expanduser('~/.config/iem.at/MINTmix.conf'),
              ])
_smConf=_getDict(_config, _smDefaults['/id'])
_smConf['/id']=_smDefaults['/id']

_smConfs=dict()


###
# public accessors
def getSM(id=None):
    """get config dict for MINTsm"""
    if (id is None) or (id == _smConf['/id']):
        print "default SMconf", id
        return _smConf
    else:
        if _smConfs.has_key(id):
            print "cached conf"
            return _smConfs[id]
        d=_getDict(_config, id)
        d['/id']=id
        _smConfs[id]=d
        return d

def getMIX():
    """get config dict for MINTmix"""
    return _mixConf

def write(name):
    config=ConfigParser.ConfigParser()
    _setDict(config, 'MIX', _mixConf)
    _setDict(config, 'SM' , _smDefaults)
    _setDict(config, _smDefaults['/id'], _smConf)
    for id in _smConfs:
        _setDict(config, id, _smConfs[id])
    with open(name, 'wb') as f:
        config.write(f)
        
#
####################################################


if __name__ == '__main__':
    m=getMIX()
    print "MIX: ", m
    print "SMi: ", getSM()
    print "foo: ", getSM('foo')

    write('foo.config')
