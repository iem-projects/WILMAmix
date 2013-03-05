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

import os
import time
from threading import Thread

class SystemHealth:
    class SystemHealthThread(Thread):
        try:
            import psutil
            have_psutil = True
        except ImportError:
            have_psutil = False
            print "failed to import 'psutil'. do you have 'python-psutil' installed?"

        SMBUS_gaugeAddr                = 0x0b
        SMBUS_cmdRelativeStateOfCharge = 0x0d
        SMBUS_cmdRunTimeToEmpty        = 0x11
        SMBUS_cmdAverageTimeToEmpty    = 0x13
        SMBUS_cmdBatteryStatus         = 0x16

        def __init__(self, interval=1.0, path=None):
            Thread.__init__(self)
            self.setDaemon(True)
            try:
                if path is None:
                    path='.'
                os.statvfs(path)
                self.path=path
            except None:
                self.path=os.path.expanduser('~')

            try:
                from smbus import SMBus
                self.smbus = SMBus(3)
            except ImportError as e:
                self.smbus = None
                print "failed to import 'smbus'. do you have 'python-smbus' installed?"
                print e
            except IOError as e:
                self.smbus = None
                print "failed to connect to SMBus. is the user member of the 'i2c' group?"
                print e

            self.interval=interval
            self.cpu = 1.
            self.mem = 1.
            self.disk= 1.
            self.battery = 1.
            self.runtime = 0
            self.last=0

            self.keepRunning=True
            self.isRunning=False

        def run(self):
            if SystemHealth.SystemHealthThread.have_psutil:
                psutil=SystemHealth.SystemHealthThread.psutil
            else:
                psutil=None
            while self.keepRunning:
                self.isRunning=True
                now=time.time()

                s=os.statvfs(self.path)
                self.disk=(s.f_blocks-s.f_bfree)*1./s.f_blocks

                ## CPU,...
                if psutil is not None:
                    used=psutil.used_phymem()
                    avail=psutil.avail_phymem()
                    #self.mem=psutil.phymem_usage().percent/100.
                    self.mem=(1.0*used)/(used+avail)

                    self.cpu=psutil.cpu_percent(interval=self.interval)/100.

                ### battery
                if self.smbus is not None:
                    try:
                        charge  = self.smbus.read_word_data(SystemHealth.SystemHealthThread.SMBUS_gaugeAddr, SystemHealth.SystemHealthThread.SMBUS_cmdRelativeStateOfCharge)
                        runtime = self.smbus.read_word_data(SystemHealth.SystemHealthThread.SMBUS_gaugeAddr, SystemHealth.SystemHealthThread.SMBUS_cmdRunTimeToEmpty)
                        state   = self.smbus.read_word_data(SystemHealth.SystemHealthThread.SMBUS_gaugeAddr, SystemHealth.SystemHealthThread.SMBUS_cmdBatteryStatus)
                    except IOError:
                        charge=0.
                        runtime=0.
                        pass # hopefully a temporary error...
                    

                    self.battery = charge/100.
                    self.runtime = runtime

                deltime = self.interval - (time.time()-now)
                if deltime > 0.:
                    time.sleep(deltime)

            ## loop finished
            self.isRunning=False

    def __init__(self, interval=1.0, path=None):
        self.thread = SystemHealth.SystemHealthThread(interval, path)
        self.cpu = 1.
        self.mem = 1.
        self.disk= 1.
        self.battery = 1.
        self.runtime = 0
        self.thread.start()
        while not (self.thread.keepRunning and self.thread.isRunning):
            time.sleep(0.1)
        self.update()
    def __del__(self):
        self.stop()
    def stop(self):
        if self.thread is not None:
            self.thread.keepRunning = False
            self.thread.join()
            self.thread=None
    def update(self):
        if self.thread is not None:
            self.cpu  = self.thread.cpu
            self.mem  = self.thread.mem
            self.disk = self.thread.disk
            self.battery = self.thread.battery
            self.runtime = self.thread.runtime
        else:
            self.cpu = 1.
            self.mem = 1.
            self.disk= 1.
            self.battery = 1.
            self.runtime = 0

######################################################################

if __name__ == '__main__':
    print "SystemHealth..."
    s=SystemHealth()
    try:
        print "CPU: ", s.cpu
        print "MEM: ", s.mem
        print "DISK: ", s.disk
        print "BAT: ", s.battery
        print "runtime: ",s.runtime
        time.sleep(5)
        s.update()
        print "CPU: ", s.cpu
        print "MEM: ", s.mem
        print "DISK: ", s.disk
        print "BAT: ", s.battery
        print "runtime: ",s.runtime
    except KeyboardInterrupt:
        print "shutting down"
    s.stop()
