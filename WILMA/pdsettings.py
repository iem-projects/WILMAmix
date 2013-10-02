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

###
## parse the contents of the pdsettings file into a dict
## merge multiple dicts in a meaningful way
## generate Pd-arguments from the dict
###

# sample pdsettings
## audioapi: 5
## noaudioin: False
## audioindev1: 0 2
## noaudioout: False
## audiooutdev1: 0 2
## audiobuf: 25
## rate: 48000
## callback: 0
## blocksize: 64
## nomidiin: False
## midiindev1: 0
## midiindev2: 0
## nomidiout: False
## midioutdev1: 18
## midioutdev2: 0
## midioutdev3: 0
## midioutdev4: 0
## npath: 0
## standardpath: 1
## verbose: 0
## loadlib1: Gem
## nloadlib: 1
## defeatrt: 0
## flags: 

#arguments
## -r <n>           -- specify sample rate
## -audioindev ...  -- audio in devices; e.g., "1,3" for first and third
## -audiooutdev ... -- audio out devices (same)
## -audiodev ...    -- specify input and output together
## -inchannels ...  -- audio input channels (by device, like "2" or "16,8")
## -outchannels ... -- number of audio out channels (same)
## -channels ...    -- specify both input and output channels
## -audiobuf <n>    -- specify size of audio buffer in msec
## -blocksize <n>   -- specify audio I/O block size in sample frames
## -sleepgrain <n>  -- specify number of milliseconds to sleep when idle
## -nodac           -- suppress audio output
## -noadc           -- suppress audio input
## -noaudio         -- suppress audio input and output (-nosound is synonym) 
## -listdev         -- list audio and MIDI devices
## -oss             -- use OSS audio API
## -alsa            -- use ALSA audio API
## -alsaadd <name>  -- add an ALSA device name to list
## -jack            -- use JACK audio API
## -pa              -- use Portaudio API
## -midiindev ...   -- midi in device list; e.g., "1,3" for first and third
## -midioutdev ...  -- midi out device list, same format
## -mididev ...     -- specify -midioutdev and -midiindev together
## -nomidiin        -- suppress MIDI input
## -nomidiout       -- suppress MIDI output
## -nomidi          -- suppress MIDI input and output
## -alsamidi        -- use ALSA midi API
## -path <path>     -- add to file search path
## -nostdpath       -- don't search standard ("extra") directory
## -stdpath         -- search standard directory (true by default)
## -helppath <path> -- add to help file search path
## -open <file>     -- open file(s) on startup
## -lib <file>      -- load object library(s)
## -font-size <n>     -- specify default font size in points
## -font-face <name>  -- specify default font
## -font-weight <name>-- specify default font weight (normal or bold)
## -verbose         -- extra printout on startup and when searching for files
## -d <n>           -- specify debug level
## -noloadbang      -- suppress all loadbangs
## -stderr          -- send printout to standard error instead of GUI
## -nogui           -- suppress starting the GUI
## -guiport <n>     -- connect to pre-existing GUI over port <n>
## -guicmd "cmd..." -- start alternatve GUI program (e.g., remote via ssh)
## -send "msg..."   -- send a message at startup, after patches are loaded
## -noprefs         -- suppress loading preferences on startup
## -rt or -realtime -- use real-time priority
## -nrt             -- don't use real-time priority
## -nosleep         -- spin, don't sleep (may lower latency on multi-CPUs)
## -schedlib <file> -- plug in external scheduler
## -extraflags <s>  -- string argument to send schedlib
## -batch           -- run off-line as a batch process
## -noautopatch     -- defeat auto-patching new from selected objects
## -compatibility <f> -- set back-compatibility to version <f>

# dictionary
## 'audioapi'     = (string))'jack'
## 'audiocallback'= (bool)False
## 'audioin'      = None, (int)2, (int[])
## 'audioout'     = None, (int)2, (int[])
## 'audiobuffer'  = (int)25
## 'audiorate'    = (int)rate
## 'audioblocksize'= (int)64

## 'sleepgrain'   = None(=-nosleep), (int)
## 'alsaadd'      = (string[])

## 'midiapi'      = (string)'alsa'
## 'midiin'       = None, (int[])
## 'midiout'      = None, (int[])
## 'standardpath' = (bool)True
## 'verbose'      = (bool)False
## 'debug'        = (int)0
## 'realtime'     = (bool)True
## 'lib'          = (string[])
## 'path'         = (string[])
## 'loadbang'     = (bool)True
## 'stderr'       = (bool)False
## 'send'         = (string[])
## 'helppath'     = (string[])
## 'patch'        = (string[])
## 'batch'        = (bool)False
## 'autopatch'    = (bool)True
## 'compatibility'= (float)0.44
## 'gui'          = None, (string)"guicmd"
## 'guiport'      = (int)
## 'schedlib'     = (string)
## 'schedflags'   = (string)
## 'font.size'    = (int)
## 'font.face'    = (string)
## 'font.weight'  = (string)

def _audioAPI = {
    ## pdsettings-file to API
    0: 'None',
    1: 'ALSA',
    2: 'OSS',
    3: 'MMIO',
    4: 'PORTAUDIO',
    5: 'JACK',
    6: 'SGI',
    7: 'AUDIOUNIT',
    8: 'ESD',
    9: 'DUMMY',
    ## cmdline-flag to API
    '-alsa': 'ALSA',
    '-oss' : 'OSS',
    '-mmio': 'MMIO',
    '-pa'  : 'PORTAUDIO',
    '-asio': 'PORTAUDIO',
    '-jack': 'JACK',
    '-audiounit': 'AUDIOUNIT',
    '-esd' : 'ESD',

    ## API to cmdline-flag
    'ALSA'     : '-alsa',
    'OSS'      : '-oss',
    'MMIO'     : '-mmio',
    'PORTAUDIO': '-pa',
    'JACK'     : '-jack',
    'AUDIOUNIT': '-audiounit',
    'ESD'      : '-esd',
}
def _argRate(d, arg):
    d['audiorate']=int(arg)
def _argAudioInDev(d, arg):
    d['audioin']=arg
def _argAudioOutDev(d, arg):
    d['audioout']=arg
def _argAudioDev(d, arg):
    _argAudioInDev(d, arg)
    _argAudioOutDev(d, arg)
def _argInChannels(d, arg):
    d['inchannels']=int(arg)
def _argOutChannels(d, arg):
    d['outchannels']=int(arg)
def _argChannels(d, arg):
    _argInChannels(d, arg)
    _argOutChannels(d, arg)
def _argAudiobuf(d, arg):
    d['audiobuffer']=int(arg)
def _argBlocksize(d, arg):
    d['audioblocksize']=int(arg)
def _argSleepgrain(d, arg):
    d['sleepgrain']=int(arg)
def _argAlsaAdd(d, arg):
    if d['alsadevice'] is None:
        d['alsadevice']=[]
    d['alsadevice']+=[arg]
def _argMidiInDev(d, arg):
    d['midiindev']=arg
def _argMidiOutDev(d, arg):
    d['midioutdev']=arg
def _argMidiDev(d, arg):
    _argMidiInDev(d, arg)
    _argMidiOutDev(d, arg)
def _argPath(d, arg):
    if d['path'] is None:
        d['path']=[]
    d['path']+=[arg]
def _argHelpPath(d, arg):
    if d['helppath'] is None:
        d['helppath']=[]
    d['helppath']+=[arg]
def _argOpen(d, arg):
    if d['patch'] is None:
        d['patch']=[]
    d['patch']+=[arg]
def _argLib(d, arg):
    if d['lib'] is None:
        d['lib']=[]
    d['lib']+=[arg]
def _argFontSize(d, arg):
    d['font.size']=int(arg)
def _argFontFace(d, arg):
    d['font.face']=arg
def _argFontWeight(d, arg):
    d['font.weight']=arg
def _argD(d, arg):
    d['d']=int(arg)
def _argGuiPort(d, arg):
    d['guiport']=int(arg)
def _argGuiCmd(d, arg):
    d['guicmd']=arg
def _argSend(d, arg):
    if d['send'] is None:
        d['send']=[]
    d['send']+=[arg]
def _argSchedlib(d, arg):
    d['schedlib']=arg
def _argExtraFlags(d, arg):
    d['schedflags']=arg
def _argCompatibility(d, arg):
    d['compatibility']=float(arg)

_subflagDict = {
    '-rate': _argRate,
    '-audioindev': _argAudioindev,
    '-audiooutdev': _argAudiooutdev,
    '-audiodev': _argAudiodev,
    '-inchannels': _argInChannels,
    '-outchannels': _argOutChannels,
    '-channels': _argChannels,
    '-audiobuf': _argAudiobuf,
    '-blocksize': _argBlocksize,
    '-sleepgrain': _argSleepgrain,
    '-alsaadd': _argAlsaAdd,
    '-midiindev': _argMidiInDev,
    '-midioutdev': _argMidiOutDev,
    '-mididev': _argMidiDev,
    '-path': _argPath,
    '-helppath': _argHelpPath,
    '-open': _argOpen,
    '-lib': _argLib,
    '-font-size': _argFontSize,
    '-font-face': _argFontFace,
    '-font-weight': _argFontWeight,
    '-d': _argD,
    '-guiport': _argGuiPort,
    '-guicmd': _argGuiCmd,
    '-send': _argSend,
    '-schedlib': _argSchedLib,
    '-extraflags': _argExtraFlags,
    '-compatibility': _argCompatibility,
    }


def parseArgs(args):
    d=dist()
    subParser=None
    for a in args:
        if subParser:
            subParser(d, a)
        if a in _subflagDict:
            subParser=_subflagDict[a]
        else if a in _audioapis:
            pass
        else:
            if '-nodac' == a:
                pass
            if '-noadc' == a:
                pass
            if '-noaudio' == a:
                pass
            if '-nomidiin' == a:
                pass
            if '-nomidiout' == a:
                pass
            if '-nomidi' == a:
                pass
            if '-alsamidi' == a:
                pass
            if '-nostdpath' == a:
                pass
            if '-stdpath' == a:
                pass
            if '-verbose' == a:
                pass
            if '-noloadbang' == a:
                pass
            if '-stderr' == a:
                pass
            if '-nogui' == a:
                pass
            if '-noprefs' == a:
                pass
            if '-rt' == a:
                pass
            if '-realtime' == a:
                pass
            if '-nrt' == a:
                pass
            if '-nosleep' == a:
                d['sleepgrain']=None
            if '-batch' == a:
                pass
            if '-noautopatch' == a:
                pass

    return d
def parseFile(filename):
    d=dict()
    with open(filename, 'r') as f:
        content = f.read()

    return d

class pdsettings:
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
            pd = pdsettings(arg)
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



