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
## 'audioin'      = None, [(int)0, (int)2][]
## 'audioout'     = None, [(int)0, (int)2][]
## 'audiobuffer'  = (int)25
## 'audiorate'    = (int)rate
## 'audioblocksize'= (int)64

## 'sleepgrain'   = None(=-nosleep), (int)
## 'alsadevice'   = (string[])

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

_audioAPI = {
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
    ## API to cmdline-flag
    'ALSA'     : '-alsa',
    'OSS'      : '-oss',
    'MMIO'     : '-mmio',
    'PORTAUDIO': '-pa',
    'JACK'     : '-jack',
    'AUDIOUNIT': '-audiounit',
    'ESD'      : '-esd',
}
_audioAPIflag = {
    ## cmdline-flag to API
    '-alsa': 'ALSA',
    '-oss' : 'OSS',
    '-mmio': 'MMIO',
    '-pa'  : 'PORTAUDIO',
    '-asio': 'PORTAUDIO',
    '-jack': 'JACK',
    '-audiounit': 'AUDIOUNIT',
    '-esd' : 'ESD',
}
def truism(S):
    try: return bool(int(S))
    except ValueError: pass
    s=S.lower()
    if s in ['true', 't', '1', 'yes', 'y']: return True
    if s in ['false', 'f', '0', 'no', 'n']: return False
    raise ValueError ('No known mapping from \'%s\' to bool' % (S))

def _argAudioDevParse(devlist, arg, index=1):
    devs=[int(x) for x in arg.split(',')]
    ## now we have the deviceIDs fill/update the 'audioin' values
    for i, v in enumerate(devs):
        try:
            devlist[i][index]=v
        except IndexError:
            if index:
                devlist+=[[None, v]]
            else:
                devlist+=[[v, None]]

    return devlist

def _argRate(d, arg):
    d['audiorate']=int(arg)
def _argAudioInDev(d, arg):
    try:   d['audioin']=_argAudioDevParse(d.get('audioin', []), arg, 0)
    except ValueError: pass
def _argAudioOutDev(d, arg):
    try:   d['audioout']=_argAudioDevParse(d.get('audioout', []), arg, 0)
    except ValueError: pass
def _argInChannels(d, arg):
    try:   d['audioin']=_argAudioDevParse(d.get('audioin', []), arg, 1)
    except ValueError: pass
    #d['inchannels']=int(arg)
def _argOutChannels(d, arg):
    try:   d['audioout']=_argAudioDevParse(d.get('audioout', []), arg, 1)
    except ValueError: pass
    #d['outchannels']=int(arg)
def _argAudioDev(d, arg):
    _argAudioInDev(d, arg)
    _argAudioOutDev(d, arg)
def _argChannels(d, arg):
    _argInChannels(d, arg)
    _argOutChannels(d, arg)
def _argAudioBuf(d, arg):
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
    if d.get('path', None) is None: d['path']=[]
    oldpath=d['path']
    for p in arg.split(':'):
        if not p in oldpath:
            oldpath+=[p]
    d['path']=oldpath
def _argHelpPath(d, arg):
    if d.get('helppath', None) is None: d['helppath']=[]
    oldpath=d['helppath']
    for p in arg.split(':'):
        if not p in oldpath:
            oldpath+=[p]
    d['helppath']=oldpath
def _argOpen(d, arg):
    if d['patch'] is None:
        d['patch']=[]
    d['patch']+=[arg]
def _argLib(d, arg):
    if d.get('lib', None) is None: d['lib']=[]
    oldlibs=d['lib']
    for l in arg.split(':'):
        if not l in oldlibs:
            oldlibs+=[l]
    d['lib']=oldlibs
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
    d['gui']=arg
def _argSend(d, arg):
    if d['send'] is None:
        d['send']=[]
    d['send']+=[arg]
def _argSchedLib(d, arg):
    d['schedlib']=arg
def _argExtraFlags(d, arg):
    d['schedflags']=arg
def _argCompatibility(d, arg):
    d['compatibility']=float(arg)

_subflagDict = {
    '-rate': _argRate,
    '-audioindev': _argAudioInDev,
    '-audiooutdev': _argAudioOutDev,
    '-audiodev': _argAudioDev,
    '-inchannels': _argInChannels,
    '-outchannels': _argOutChannels,
    '-channels': _argChannels,
    '-audiobuf': _argAudioBuf,
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


def parseArgs(args, result=dict()):
    subParser=None
    if isinstance(args, basestring):
        ## splitargs into an array
        ## the following is a bit naive, as it cannot parse e.g. '-send "foo bar"'
        args=args.split()

    for a in args:
        if subParser:
            subParser(result, a)        ## value for argument
            subParser=None
        elif a in _subflagDict:  ## check whether this argument takes a value
            subParser=_subflagDict[a]
        elif a in _audioAPIflag: ## check whether this is a known flag setting the audio-API
            result['audioapi']=_audioAPIflag[a]
        else: ## no, this is a no-argument flag
            if '-nodac' == a:
                result['audioout']=None
            elif '-noadc' == a:
                result['audioin'] =None
            elif '-noaudio' == a:
                result['audioout']=None
                result['audioin'] =None
            elif '-nosound' == a:
                result['audioout']=None
                result['audioin'] =None
            elif '-nomidiin' == a:
                result['midiin'] =None
            elif '-nomidiout' == a:
                result['midiout']=None
            elif '-nomidi' == a:
                result['midiin'] =None
                result['midiout']=None
            elif '-alsamidi' == a:
                result['midiapi']='ALSA'
            elif '-defaultmidi' == a: ## dummy-arg
                result.pop('midiapi', None)

            elif '-nostdpath' == a:
                result['standardpath']=False
            elif '-stdpath' == a:
                result['standardpath']=True

            elif '-verbose' == a:
                result['verbose']=True
            elif '-noverbose' == a: ## dummy-arg
                result['verbose']=False

            elif '-noloadbang' == a:
                result['loadbang']=False
            elif '-loadbang' == a: ## dummy-arg
                result['loadbang']=True

            elif '-stderr' == a:
                result['stderr']=True
            elif '-nostderr' == a: ## dummy-arg
                result['stderr']=False

            elif '-nogui' == a:
                result['gui']=None
            elif '-gui' == a: ## dummy-arg
                result.pop('gui', None)

            elif '-noprefs' == a:
                result['preferences']=False
            elif '-prefs' == a: ## dummy-arg
                result['preferences']=True

            elif '-rt' == a:
                result['realtime']=True
            elif '-realtime' == a:
                result['realtime']=True
            elif '-nrt' == a:
                result['realtime']=False

            elif '-nosleep' == a:
                result['sleepgrain']=None

            elif '-batch' == a:
                result['batch']=True
            elif '-nobatch' == a: ## dummy-arg
                result['batch']=False

            elif '-noautopatch' == a:
                result['autopatch']=False
            elif '-autopatch' == a: ## dummy-arg
                result['autopatch']=True

    return result

def _fileEnum(d, prefix, count):
    result=[]
    for id in range(count):
        try:   result+=[d[prefix+str(id+1)]]
        except KeyError: pass
    return result
def _fileDisableAM(result, key, disabled):
    if disabled:
        result[key]=None
    elif result.get(key, False) is None:
        ## if 'audiout' is set and 'None', delete it; else leave unchanged
        result.pop(key, None)
def _fileDevices(d, prefix):
    result=[]
    for i in range(8):
        dev=d.get(prefix+str(i+1), None)
        if dev:
            try:
                result+=[[int(x) for x in dev.split()]]
            except ValueError:
                pass
    return result

def parseArgFile(filename=None, result=dict()):
    if filename is None:
        import os.path
        filename=os.path.join(os.path.expanduser('~'), '.pdrc')

    try:
        with open(filename, 'r') as f:
            content = f.readlines()
    except IOError:
        ## file not found or unreadable
        return result
    arr=[]
    for l in content:
        if l.startswith('#'): ## ignore comments
            continue
        try:
            x,y=l.split(' ', 1)
            arr.append(x)
            arr.append(y.strip())
        except ValueError:
            arr.append(l.strip())
    return parseArgs(arr, result)

def parseFile(filename=None, result=dict()):
    d=dict()
    if filename is None:
        import os.path
        filename=os.path.join(os.path.expanduser('~'), '.pdsettings')

    try:
        with open(filename, 'r') as f:
            content = f.readlines()
    except IOError:
        ## file not found or unreadable
        return result
    for l in content:
        if l.startswith('#'): ## ignore comments
            continue
        x,y=l.split(':', 1)
        d[x.strip()]=y.strip()

    ## audio
    try: result['audiorate']=int(d['rate'])
    except (KeyError, ValueError): pass
    try: result['audiobuffer']=int(d['audiobuf'])
    except (KeyError, ValueError): pass
    try: result['audioblocksize']=int(d['blocksize'])
    except (KeyError, ValueError): pass
    try: result['audioapi']=_audioAPI[int(d['audioapi'])]
    except (KeyError, ValueError): pass
    try: result['audiocallback']=bool(int(d['callback']))
    except (KeyError, ValueError): pass

    try: _fileDisableAM(result, 'audioin', truism(d['noaudioin']))
    except (KeyError, ValueError): pass
    try: _fileDisableAM(result, 'audioout', truism(d['noaudioout']))
    except (KeyError, ValueError): pass

    try:
        devs=_fileDevices(d, 'audioindev')
        if(devs):result['audioin']=devs
    except (KeyError): pass
    try:
        devs=_fileDevices(d, 'audiooutdev')
        if(devs):result['audioout']=devs
    except (KeyError): pass


    ## midi
    try: _fileDisableAM(result, 'midiin', truism(d['nomidiin']))
    except (KeyError, ValueError): pass
    try: _fileDisableAM(result, 'midiout', truism(d['nomidiout']))
    except (KeyError, ValueError): pass

    ## boolean flags
    try: result['standardpath']=bool(int(d['standardpath']))
    except (KeyError, ValueError): pass
    try: result['verbose']=bool(int(d['verbose']))
    except (KeyError, ValueError): pass
    try: result['realtime']=not bool(int(d['defeatrt']))
    except (KeyError, ValueError): pass
    ## arrays
    try:
        count=int(d['nloadlib'])
        if count>0:
            if not 'lib' in result:
                result['lib']=[]
            result['lib']+=_fileEnum(d, 'loadlib', count)
    except (KeyError, ValueError) as e:
        pass
    try:
        count=int(d['npath'])
        if count>0:
            if not 'path' in result:
                result['path']=[]
        result['path']+=_fileEnum(d, 'path', count)
    except (KeyError, ValueError): pass

    try:   parseArgs(d['flags'], result)
    except KeyError: pass

    return result

def getArgs(settings, audio=True, midi=True, gui=True, misc=True):
    result=[]
    if audio:
        v=settings.get('audioapi', None)
        if v: result+=[_audioAPI[v]]

        v=settings.get('audiocallback', None)
        if v: pass ## not available as cmdline arg!

        try:
            v=settings['audioin']
            if not v: result+=['-noadc']
            else:
                channels=None
                devices=None
                for i in v:
                    if i[0] is None and i[1] is None: continue
                    if devices: devices+=','+str(i[0])
                    else: devices=str(i[0])
                    if i[1] is None:
                        c='0'
                    else:
                        c=str(i[1])
                    if channels: channels+=','+c
                    else: channels=c
                if devices: result+=['-audioindev', devices]
                if channels: result+=['-inchannels', channels]
        except KeyError: pass
        try:
            v=settings['audioout']
            if not v: result+=['-noadc']
            else:
                channels=None
                devices=None
                for i in v:
                    if i[0] is None and i[1] is None: continue
                    if devices: devices+=','+str(i[0])
                    else: devices=str(i[0])
                    if i[1] is None:
                        c='0'
                    else:
                        c=str(i[1])
                    if channels: channels+=','+c
                    else: channels=c
                if devices: result+=['-audiooutdev', devices]
                if channels: result+=['-outchannels', channels]
        except KeyError: pass

        v=settings.get('audiobuffer', None)
        if v: result+=['-audiobuf', str(v)]

        v=settings.get('audioblocksize', None)
        if v: result+=['-blocksize', str(v)]

        v=settings.get('audiorate', None)
        if v: result+=['-r', str(v)]

        v=settings.get('alsadevice', [])
        for d in v:
            result+=['-alsaadd', d]

        v=settings.get('realtime', None)
        if v is not None:
            if v: result+=['-rt']
            else: result+=['-nrt']

    if midi:
       v=settings.get('midiapi', None)
       if 'ALSA'==v: result+=['-alsamidi']

       try:
           v=settings['midiin']
           if not v:
               result+=['-nomidiin']
           else:
               devices=None
               for i in v:
                   if i:
                       if devices: devices+=','+str(i)
                       else: devices=str(i)
               if devices:
                   result+=['-midiin', devices]
       except KeyError:pass
       try:
           v=settings['midiout']
           if not v:
               result+=['-nomidiout']
           else:
               devices=None
               for i in v:
                   if i:
                       if devices: devices+=','+str(i)
                       else: devices=str(i)
               if devices:
                   result+=['-midiout', devices]
       except KeyError:pass

    if gui:
        try:
            v=settings['gui']
            if v: result+=['-guicmd', str(v)]
            else: result+=['-nogui']
        except KeyError: pass
        v=settings.get('guiport', None)
        if v: result+=['-guiport', str(v)]

        v=settings.get('font.size', None)
        if v: result+=['-font-size', str(v)]
        v=settings.get('font.face', None)
        if v: result+=['-font-face', str(v)]
        v=settings.get('font.weight', None)
        if v: result+=['-font-weight', str(v)]

    if misc:
        v=settings.get('standardpath', None)
        if v is not None:
            if v: result+=['-stdpath']
            else: result+=['-nostdpath']

        v=settings.get('verbose', None)
        if v: result+=['-verbose']

        v=settings.get('debug', None)
        if v: result+=['-d', str(v)]

        v=settings.get('loadbang', True)
        if not v: result+=['-noloadbang']

        v=settings.get('stderr', False)
        if v: result+=['-stderr']

        v=settings.get('batch', False)
        if v: result+=['-batch']

        v=settings.get('autopatch', True)
        if not v: result+=['-noautopatch']

        v=settings.get('compatibility', None)
        if v is not None: result+=['-compatibility', str(v)]

        v=settings.get('schedlib', None)
        if v: result+=['-schedlib', str(v)]
        v=settings.get('schedflags', False)
        if v: result+=['-extraflags']

        try:
            v=settings['sleepgrain']
            if v is None:
                result+=['-nosleep']
            else:
                result+=['-sleepgrain', str(v)]
        except KeyError: pass

        v=settings.get('path', None)
        if v: result+=['-path', ':'.join(v)]
        v=settings.get('lib', None)
        if v: result+=['-lib', ':'.join(v)]
        v=settings.get('helppath', None)
        if v: result+=['-helppath', ':'.join(v)]

        v=settings.get('send', [])
        for i in v: result+=['-send', i]
        v=settings.get('patch', [])
        for i in v: result+=['-open', i]

    return result

######################################################################

if __name__ == '__main__':
    import sys
    print("DEFAULTARGS: %s" % (parseFile()))
    for arg in sys.argv[1:]:
        try:
            pd = parseArgs(getArgs(parseFile(arg), audio=True, midi=False, misc=False, gui=False))

            pdargs=''
            #pdargs='-lib zexy:iemmatrix:Gem -path foo -stderr -audioindev 5,2 -channels 42 -path foo'
            #pdargs='-lib zexy:iemmatrix:Gem -path foo -stderr  -path foo'
            pdargs='-lib zexy:iemmatrix -stderr'
            pd = parseArgs(pdargs, pd)
            for key in pd:
                print ("%s: %s" % (key, pd[key]))

            args=getArgs(pd, audio=True, midi=True, misc=True, gui=False)
            print("ARGS: %s" % (args))
        except int: pass
        #except:
        #    print "unable to open file: ", arg



