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
from threading import Thread

## NOTE: wait longer!


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

def _getGAUGE(smbus, sleep=1.0):
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
        time.sleep(sleep)
        runtime = smbus.read_word_data(gaugeAddr,
                                            cmdRunTimeToEmpty)
        time.sleep(sleep)
        state   = smbus.read_word_data(gaugeAddr,
                                            cmdBatteryStatus)
        time.sleep(sleep)
    except IOError as e:
        exception=e
        pass # hopefully a temporary error...

    return (charge/100., runtime, state)


def _getPIC(smbus, sleep=1.0):
    ## SMBus constants
    picAddr                  = 0x0e
    cmdTemperature           = 0xbb
    cmdSyncStatus            = 0xcc
    cmdGetRSSI               = 0xaa
    cmdGetPacketLoss         = 0xdd

    ## defaults
    temperature = 0
    packetlost=0
    rssi=0
    syncstatus=0x0

    try:
        temperature = smbus.read_byte_data(picAddr,
                                               cmdTemperature)
        time.sleep(sleep)

        packetlost  = smbus.read_byte_data(picAddr,
                                                cmdGetPacketLoss)
        time.sleep(sleep)

        rssi        = smbus.read_byte_data(picAddr,
                                                cmdGetRSSI)
        time.sleep(sleep)

        syncstatus  = smbus.read_byte_data(picAddr,
                                                cmdSyncStatus)
        time.sleep(sleep)

        sync_external = (syncstatus & 0x01)!=0
        sync_internal = (syncstatus & 0x02)!=0

##        if(0x01==syncstatus): # syncing
##            sync_external=True
##            sync_internal=False
##        elif(0x02==syncstatus): # freerunning
##            sync_external=False
##            sync_internal=True
##        elif(0x03==syncstatus): # synced
##            sync_external=True
##            sync_internal=True
##        else: ## ouch
##            sync_external=False
##            sync_internal=False
    except IOError as e:
        pass # hopefully a temporary error...
    temp=(temperature/2.0) - 10.0
    if packetlost != 0:
        packetRatio = 100./packetlost
    else:
        packetRatio = 0.
    return (temp, packetRatio, rssi-107., (sync_external, sync_internal))

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

            self.keepRunning=True
            self.isRunning=False

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
            while self.keepRunning:
                self.isRunning=True
                now=time.time()
                ### battery
                if smbus is not None:
                    (self.battery, self.runtime, state) = _getGAUGE(smbus)
                    (self.temperature, self.packetRatio, self.rssi, (self.sync_external, self.sync_internal)) = _getPIC(smbus)

                deltime = self.interval - (time.time()-now)
                if deltime > 0.:
                    time.sleep(deltime)


    class SystemHealthThread(Thread):
        try:
            import psutil
            have_psutil = True
        except ImportError:
            have_psutil = False
            logging.fatal("failed to import 'psutil'. do you have 'python-psutil' installed?")

        def __init__(self, interval=1.0, intervalSM=60.0, path=None):
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

            try:
                from smbus import SMBus
                self.smbus = SMBus(3)
            except ImportError:
                self.smbus = None
                logging.exception("failed to import 'smbus'. do you have 'python-smbus' installed?")
            except IOError:
                self.smbus = None
                logging.exception("failed to connect to SMBus. is the user member of the 'i2c' group?")

            self.interval=interval
            self.cpu = 1.
            self.mem = 1.
            self.disk= 1.
            self.battery = 1.
            self.runtime = 0
            self.last=0
            self.sync_external = True # just for testing
            self.sync_internal  = False
            self.temperature = 0.
            self.packetRatio = 0.
            self.rssi = 0.

            self.keepRunning=True
            self.isRunning=False

            self.lastSM=0
            self.intervalSM = intervalSM

        def run(self):
            if systemhealth.SystemHealthThread.have_psutil:
                psutil=systemhealth.SystemHealthThread.psutil
            else:
                psutil=None
            while self.keepRunning:
                self.isRunning=True
                now=time.time()
                try:
                    s=os.statvfs(self.path)
                    ## (blocks-bfree) does is inaccurate
                    ## self.disk=(s.f_blocks-s.f_bfree)*1./s.f_blocks
                    ## this is more accurate
                    self.disk=(s.f_blocks-s.f_bavail)*1./s.f_blocks
                except OSError:
                    try:
                        os.makedirs(self.path)
                    except OSError:
                        if not os.path.isdir(self.path):
                            raise

                ## CPU,...
                if psutil is not None:
                    self.mem=_getMEM(psutil)
                    self.cpu=_getCPU(psutil, self.interval)

                ### battery
                if self.smbus is not None:
                    if ((now-self.lastSM) >= self.intervalSM):
                        self.lastSM=now

                        (self.battery, self.runtime, state) = _getGAUGE(self.smbus)
                        (self.temperature, self.packetRatio, self.rssi, (self.sync_external, self.sync_internal)) = _getPIC(self.smbus)

                deltime = self.interval - (time.time()-now)
                if deltime > 0.:
                    time.sleep(deltime)

            ## loop finished
            self.isRunning=False

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

        self.thread.start()
        while not (self.thread.keepRunning and self.thread.isRunning):
            time.sleep(0.1)

        self.smthread.start()
        while not (self.smthread.keepRunning and self.smthread.isRunning):
            time.sleep(0.1)


        self.update()
    def __del__(self):
        self.stop()
    def stop(self):
        if self.thread is not None:
            self.thread.keepRunning = False
            self.thread.join()
            self.thread=None
        if self.smthread is not None:
            self.smthread.keepRunning = False
            self.smthread.join()
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
