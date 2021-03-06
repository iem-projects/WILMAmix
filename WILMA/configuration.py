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

import logging as logging_
logging = logging_.getLogger('WILMA.configuration')
import socket
import ConfigParser
import os.path

def getRoot(file=None):
  if file is None:
      file='.'
  me=os.path.abspath(file)
  drive,path=os.path.splitdrive(me)
  while 1:
    path,folder=os.path.split(path)
    if not folder:
       break
  return drive+path

## files listed LATER can overwrite values from earlier files
_configpaths=[
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config'), ## built-in
    os.path.join(getRoot(), 'etc', 'WILMA'),                            ## system-wide
    os.path.join(os.path.expanduser('~'), '.config', 'wilma.iem.at'),   ## per-user
    '.',                                                                ## local
    ]

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

_version=None
def _getVersion():
  global _version, _configpaths

  if _version is not None:
    return _version
  ## check for VERSION file in the config-directories
  versionfiles=[os.path.join(path, "VERSION") for path in _configpaths]

  for vf in versionfiles:
    try:
      with open(vf) as f:
        _version=''.join(f.read().split('\n'))
    except IOError:
      pass

  ## there's no 'version.txt' file, try to guess the version from git
  if(_version is None):
    try:
      from subprocess import Popen, PIPE

      ## get short-hash from git
      gitproc = Popen(['git', 'describe', '--always'], stdout = PIPE)
      (stdout, stderr) = gitproc.communicate()
      _version=''.join(stdout.split('\n'))

      ## check for modified files
      gitproc = Popen(['git', 'status', '--porcelain'], stdout = PIPE)
      (stdout, stderr) = gitproc.communicate()
      for line in stdout.split('\n'):
        if line and (line[0] != ' ' or line[1] != ' '):
          _version+='*'
          break
    except OSError:
      pass

  if(_version is None):
    return '(unknown)'
  return _version
        
## DEFAULT values
# use STRING type for everything (even for numbers)
# they will be converted to numbers automatically in the _getDict() functions
_config=None
_smConf=None
_smConfs=dict()
_mixConf=None

def init(defaults={}):
    global _config, _smConf, _smConfs, _mixConf
    _smConfs=dict()
    mydefaults=dict()
    mydefaults['/id'      ] = socket.gethostname()
    mydefaults['/host'    ] = socket.gethostname()

    try:
        import getpass
        mydefaults['/user']=getpass.getuser()
    except ImportError:
        mydefaults['/user']='unknown'

    mydefaults['/passphrase'] = '****'

    mydefaults['/protocol'] = 'udp'
    mydefaults['/service' ] = '_wilma-sm'
    mydefaults['/port'    ] = '7777' # LATER change to 0
    mydefaults['/gain_control'] = '3' ## alsa control for mic amp

    mydefaults['/path/in' ] = '/tmp/WILMA/in'
    mydefaults['/path/out'] = '/tmp/WILMA/out'

    mydefaults['/mode'           ]='stream' # 'stream', 'record', 'process'
    mydefaults['/stream/transport/protocol']='udp'
    mydefaults['/stream/transport/port']='0'
    mydefaults['/stream/protocol']='rtp' # const
    mydefaults['/stream/profile' ]='L16' # const for now
    mydefaults['/stream/channels']='4' # const

    mydefaults['/record/timestamp/offset']='10'
    mydefaults['/record/timestamp']='0' # const
    mydefaults['/record/filename' ]='WILMA' # const

    mydefaults['/network/interface']='eth0' # ????

    mydefaults['/log/level']=str(logging.getEffectiveLevel())

    ## proxy settings
    mydefaults['/proxy/server/port']=0
    mydefaults['/proxy/client/port']=0
    mydefaults['/proxy/client/host']='localhost'

    for k in defaults:
        mydefaults[k]=defaults[k]

    configfiles=[os.path.join(path, "WILMix.conf") for path in _configpaths]

    _config = ConfigParser.ConfigParser(mydefaults)
    _config.read(configfiles)
    _mixConf=_getDict(_config, 'MIX')
    _smConf=_getDict(_config, 'SM')

    _version = _getVersion()
    _mixConf['/version'] = _version
    _smConf ['/version'] = _version

###
# public accessors
def getSM(id=None):
    """get config dict for WILMAsm"""
    if not _smConf:
        init()
    if (id is None) or (id == _smConf['/id']):
        logging.info("default SMconf %s" % id)
        return _smConf
    else:
        if _smConfs.has_key(id):
            logging.info("cached conf %s" % id)
            return _smConfs[id]
        ## FIXXME: currently we only have a single 'SM' config
        ##         if the user requests the 'special' config for a named SMi,
        ##         we just return a new *copy* (with the ID set properly)
        d=dict(_smConf)
        d['/id']=id
        _smConfs[id]=d
        return d

def getMIX():
    """get config dict for WILMix"""
    if not _mixConf:
        init()
    return _mixConf

def write(name):
    if (not _smConf) or (not _smConf):
        init()

    config=ConfigParser.ConfigParser()
    _setDict(config, 'MIX', _mixConf)
    _setDict(config, 'SM' , _smConf)
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
