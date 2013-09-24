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
logging = logging_.getLogger('WILMA.systemhealth')
import os, time
from threading import Thread, Event

## NOTE: wait longer!

def _sleep(sleep, event):
    '''sleep for a number of seconds;
       returns 'True' if processing should be interrupted ASAP'''
    if event:
        if event.wait(sleep):
            return True
    else:
        time.sleep(sleep)
    return False

def _getCPU(psutil, interval):
    percent=psutil.cpu_percent(interval=interval)
    return (percent/100.)

def _getMEM(psutil):
    used=psutil.used_phymem()
    avail=psutil.avail_phymem()
    return (1.0*used)/(used+avail)

def _getDISK(path):
    disk=0
    try:
        s=os.statvfs(path)
        ## (blocks-bfree) does is inaccurate
        ## self.disk=(s.f_blocks-s.f_bfree)*1./s.f_blocks
        ## this is more accurate
        disk=(s.f_blocks-s.f_bavail)*1./s.f_blocks
    except OSError:
        try:
            os.makedirs(path)
        except OSError:
            if not os.path.isdir(path):
                raise
    return disk

def _getGAUGE(smbus, sleep=1.0, event=None):
    ## SMBus constants
    gaugeAddr                = 0x0b
    cmdRelativeStateOfCharge = 0x0d
    cmdRunTimeToEmpty        = 0x11
    cmdAverageTimeToEmpty    = 0x13
    cmdBatteryStatus         = 0x16

    ## defaults
    charge=0.
    runtime=0.
    state=0

    exception=None
    try:
        charge  = smbus.read_word_data(gaugeAddr,
                                            cmdRelativeStateOfCharge)
        if _sleep(sleep, event):return (charge, runtime, state)

        runtime = smbus.read_word_data(gaugeAddr,
                                            cmdRunTimeToEmpty)
        if _sleep(sleep, event):return (charge, runtime, state)

        state   = smbus.read_word_data(gaugeAddr,
                                            cmdBatteryStatus)

        if _sleep(sleep, event):return (charge, runtime, state)
    except IOError as e:
        exception=e
        pass # hopefully a temporary error...

    return (charge/100., runtime, state)
def _getPIC(smbus, sleep=1.0, event=None):
    ## SMBus constants
    picAddr                  = 0x0e
    cmdTemperature           = 0xbb
    cmdSyncStatus            = 0xcc
    cmdGetRSSI               = 0xaa
    cmdGetPacketLoss         = 0xdd

    ## defaults
    temperature  =0.
    packetRatio  =0.
    rssi=-107.
    sync_internal=False
    sync_external=False

    try:
        _temp = smbus.read_byte_data(picAddr,  cmdTemperature)
        temperature=(_temp/2.0) - 10.0
        if _sleep(sleep, event):return (temperature, packetRatio, rssi, (sync_external, sync_internal))

        _packetlost  = smbus.read_byte_data(picAddr,  cmdGetPacketLoss)
        if _packetlost != 0:
            packetRatio = 100./_packetlost
        else:
            packetRatio = 0.

        if _sleep(sleep, event):return (temperature, packetRatio, rssi, (sync_external, sync_internal))

        _rssi        = smbus.read_byte_data(picAddr,  cmdGetRSSI)
        rssi=_rssi-107.
        if _sleep(sleep, event):return (temperature, packetRatio, rssi, (sync_external, sync_internal))

        _syncstatus  = smbus.read_byte_data(picAddr,  cmdSyncStatus)
##        if(0x01==_syncstatus): # syncing
##            sync_external=True
##            sync_internal=False
##        elif(0x02==_syncstatus): # freerunning
##            sync_external=False
##            sync_internal=True
##        elif(0x03==_syncstatus): # synced
##            sync_external=True
##            sync_internal=True
##        else: ## ouch
##            sync_external=False
##            sync_internal=False
        sync_external = (_syncstatus & 0x01)!=0
        sync_internal = (_syncstatus & 0x02)!=0

        _sleep(sleep, event)
    except IOError as e:
        pass # hopefully a temporary error...

    return (temperature, packetRatio, rssi, (sync_external, sync_internal))

class systemhealth:
    class SMBusThread(Thread):
        def __init__(self, interval=60.0):
            Thread.__init__(self)
            self.setDaemon(True)

            self.smbus = None
            self.interval=interval
            self.last=0

            self.battery = 1.
            self.runtime = 0
            self.sync_external = True # just for testing
            self.sync_internal  = False
            self.temperature = 0.
            self.packetRatio = 0.
            self.rssi = 0.

            self.stopEvent=Event()
            self.startEvent=Event()

            try:
                from smbus import SMBus
                self.smbus = SMBus(3)
            except ImportError:
                self.smbus = None
                logging.exception("failed to import 'smbus'. do you have 'python-smbus' installed?")
            except IOError:
                self.smbus = None
                logging.exception("failed to connect to SMBus. is the user member of the 'i2c' group?")

        def run(self):
            smbus=self.smbus
            deltime=0
            while not self.stopEvent.wait(deltime):
                self.startEvent.set()
                if not smbus:
                    return

                now=time.time()
                ### battery
                try:
                    (self.battery, self.runtime, state) = _getGAUGE(smbus, event=self.stopEvent)
                    (self.temperature, self.packetRatio, self.rssi, (self.sync_external, self.sync_internal)) = _getPIC(smbus, event=self.stopEvent)
                except ValueError:
                    logging.exception("")

                deltime = self.interval - (time.time()-now)
                if deltime <= 0.:
                    deltime = 0.
            self.startEvent.set()
        def stop(self):
            self.stopEvent.set()
            self.join()
        def start_block(self):
            self.start()
            self.startEvent.wait()

    class SystemHealthThread(Thread):
        try:
            import psutil
            have_psutil = True
        except ImportError:
            have_psutil = False
            logging.fatal("failed to import 'psutil'. do you have 'python-psutil' installed?")

        def __init__(self, interval=1.0, path=None):
            Thread.__init__(self)
            self.setDaemon(True)
            if path is None:
                path='.'
            try:
                os.makedirs(path)
            except OSError:
                if not os.path.isdir(path):
                    raise
            try:
                os.statvfs(path)
                self.path=path
            except OSError:
                logging.exception("monitoring non-existing path '%s', fallback to ~" % path)
                self.path=os.path.expanduser('~')

            self.interval=interval
            self.cpu = 1.
            self.mem = 1.
            self.disk= 1.
            self.last=0

            self.stopEvent=Event()
            self.startEvent=Event()

        def run(self):
            if systemhealth.SystemHealthThread.have_psutil:
                psutil=systemhealth.SystemHealthThread.psutil
            else:
                psutil=None
            deltime=0
            while not self.stopEvent.wait(deltime):
                self.startEvent.set()
                now=time.time()
                self.disk=_getDISK(self.path)

                ## CPU,...
                if psutil is not None:
                    self.mem=_getMEM(psutil)
                    self.cpu=_getCPU(psutil, self.interval)

                deltime = self.interval - (time.time()-now)
                if deltime <= 0.:
                    deltime=0.

            ## loop finished
            self.startEvent.set()

        def stop(self):
            self.stopEvent.set()
            self.join()
        def start_block(self):
            self.start()
            self.startEvent.wait()

    def __init__(self, interval=1.0, path=None):
        self.thread = systemhealth.SystemHealthThread(interval=interval, path=path)
        self.smthread=systemhealth.SMBusThread(interval=interval*60)

        self.cpu = 1.
        self.mem = 1.
        self.disk= 1.
        self.battery = 1.
        self.runtime = 0
        self.sync_external = False
        self.sync_internal = False
        self.temperature = 0.
        self.packetRatio = 0.
        self.rssi = 0.

        self.thread.start_block()
        self.smthread.start_block()

        self.update()
    def __del__(self):
        self.stop()
    def stop(self):
        if self.thread is not None:
            self.thread.stop()
            self.thread=None
        if self.smthread is not None:
            self.smthread.stop()
            self.smthread=None
    def update(self):
        if self.thread is not None:
            self.cpu  = self.thread.cpu
            self.mem  = self.thread.mem
            self.disk = self.thread.disk
        else:
            self.cpu = 1.
            self.mem = 1.
            self.disk= 1.

        if self.smthread is not None:
            self.battery = self.smthread.battery
            self.runtime = self.smthread.runtime
            self.sync_external = self.smthread.sync_external
            self.sync_internal = self.smthread.sync_internal
            self.temperature = self.smthread.temperature
            self.packetRatio = self.smthread.packetRatio
            self.rssi = self.smthread.rssi
        else:
            self.battery = 1.
            self.runtime = 0
            self.sync_external = True
            self.sync_internal = False
            self.temperature = 0.
            self.packetRatio = 0.
            self.rssi = 0.

######################################################################

if __name__ == '__main__':
    print "systemhealth..."
    s=systemhealth()
    def printValues(s):
        print "CPU: ", s.cpu
        print "MEM: ", s.mem
        print "DISK: ", s.disk
        print "BAT: ", s.battery
        print "runtime: ",s.runtime
        print "syncI: ", s.sync_internal
        print "syncX: ", s.sync_external
        print "temperature: ", s.temperature
        print "packetRatio: ", s.packetRatio
        print "RSSI: ", s.rssi

    try:
        printValues(s)
        time.sleep(5)
        s.update()
        printValues(s)
    except KeyboardInterrupt:
        print "shutting down"
    s.stop()
