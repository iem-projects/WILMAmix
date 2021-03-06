#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""     simpleOSC 0.2
    ixi software - July, 2006
    www.ixi-software.net

    simple API  for the Open SoundControl for Python (by Daniel Holth, Clinton
    McChesney --> pyKit.tar.gz file at http://wiretap.stetson.edu)
    Documentation at http://wiretap.stetson.edu/docs/pyKit/

    The main aim of this implementation is to provide with a simple way to deal
    with the OSC implementation that makes life easier to those who don't have
    understanding of sockets or programming. This would not be on your screen without the help
    of Daniel Holth.

    This library is free software; you can redistribute it and/or
    modify it under the terms of the GNU Lesser General Public
    License as published by the Free Software Foundation; either
    version 2.1 of the License, or (at your option) any later version.

    This library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public
    License along with this library; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

    Thanks for the support to Buchsenhausen, Innsbruck, Austria.
"""
import logging as logging_
logging = logging_.getLogger('OSC.oscAPI')
import socket
from threading import Thread

import OSC, Bundle

# globals
outSocket = 0 
addressManager = 0 
oscThread = 0




def init() :
    """ instantiates address manager and outsocket as globals
    """
    global outSocket, addressManager
    outSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    addressManager = OSC.CallbackManager()
    

def bind(func, oscaddress):
    """ bind given oscaddresses with given functions in address manager
    """
    addressManager.add(func, oscaddress)


def sendMsg(oscAddress, dataArray=[], ipAddr='127.0.0.1', port=9000, outsocket=None) :
    """create and send normal OSC msgs
        defaults to '127.0.0.1', port 9000
    """
    if outsocket is None:
        outsocket=outSocket
    outsocket.sendto( createBinaryMsg(oscAddress, dataArray),  (ipAddr, port))


def sendMsgBack(oscAddress, dataArray=[]):
    global oscThread
    oscThread.sendMsg(oscAddress, dataArray)

def sendBundleBack(bundle):
    global oscThread
    oscThread.sendBundle(bundle)


def createBundle():
    """create bundled type of OSC messages
    """
    b = OSC.OSCMessage()
    b.address = ""
    b.append("#bundle")
    b.append(0)
    b.append(0)
    return b


def appendToBundle(bundle, oscAddress, dataArray):
    """create OSC mesage and append it to a given bundle
    """
    if isinstance(bundle, Bundle.Bundle):
        bundle.append((oscAddress, dataArray))
    else:
        bundle.append( createBinaryMsg(oscAddress, dataArray),  'b')


def sendBundle(bundle, ipAddr='127.0.0.1', port=9000, outsocket=None) :
    """convert bundle to a binary and send it
    """
    if outsocket is None:
        outsocket=outSocket
    if isinstance(bundle, Bundle.Bundle):
        outsocket.sendto(bundle.data(), (ipAddr, port))
    else:
        outsocket.sendto(bundle.message, (ipAddr, port))


def createBinaryMsg(oscAddress, dataArray):
    """create and return general type binary OSC msg
    """
    m = OSC.OSCMessage()
    m.address = oscAddress

    if dataArray is None:
        dataArray=[]
    elif type(dataArray) is str:
        dataArray=[dataArray]

    try:
        for x in dataArray:  ## append each item of the array to the message
            m.append(x)
    except TypeError:
        m.append(dataArray)

    return m.getBinary() # get the actual OSC to send



################################ receive osc from The Other.

class OSCServer(Thread) :
    def __init__(self, ipAddr='127.0.0.1', port = 9001) :
        Thread.__init__(self)
        self.sender = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try :
            self.socket.bind( (ipAddr, port) )
            # self.socket.settimeout(1.0) # make sure its not blocking forever...
            self.haveSocket = True
        except socket.error :
            logging.exception( 'there was an error binding to ip %s and port %i , maybe the port is already taken by another process?' % (ipAddr, port) )
            self.haveSocket=False

    def recvFrom(self, data):
        self.sender=data[1]
        addressManager.handle(data[0], data[1])

    def run(self) :
        if self.haveSocket :
            self.isRunning = True
            while self.isRunning :
                try :
                    while 1:
                        self.recvFrom( self.socket.recvfrom(1024) ) # self.socket.recvfrom(2**13)
                except :
                    return "no data arrived" # not data arrived

    def sendMsg(self, oscAddress, dataArray=[]):
        if self.sender is not None:
            sendMsg(oscAddress, dataArray, self.sender[0], self.sender[1], self.socket)

    def sendBundle(self, bundle):
        if self.sender is not None:
            sendBundle(bundle, self.sender[0], self.sender[1], self.socket)

def listen(ipAddr='127.0.0.1', port = 9001) :
    """  creates a new thread listening to that port 
    defaults to ipAddr='127.0.0.1', port 9001
    """
    global oscThread
    oscThread = OSCServer( ipAddr, port )
    oscThread.start()
    

def dontListen() :
    """ closes the socket and kills the thread
    """
    global oscThread
    if oscThread :
        oscThread.isRunning = 0 # kill it and free the socket
        oscThread.socket.close()
        ot=oscThread
        oscThread = 0

if __name__ == '__main__':
    # example of how to use oscAPI
    # initialize address manager and sockets
    init()
    
    listen() # defaults to "127.0.0.1", 9001

    # add addresses to callback manager
    def printStuff(msg, src):
        """deals with "print" tagged OSC addresses
        """
        print "printing in the printStuff function ", msg
        print "the oscaddress is ", msg[0]
        print "the value is ", msg[2]
	print "originating from ",src

    bind(printStuff, "/test")

    #send normal msg, two ways
    sendMsg("/test", [1, 2, 3], "127.0.0.1", 9000)
    sendMsg("/test2", [1, 2, 3]) # defaults to "127.0.0.1", 9000
    sendMsg("/hello") # defaults to [], "127.0.0.1", 9000

    # create and send bundle, to ways to send
    bundle = createBundle()
    appendToBundle(bundle, "/testing/bundles", [1, 2, 3])
    appendToBundle(bundle, "/testing/bundles", [4, 5, 6])
    sendBundle(bundle, "127.0.0.1", 9000)
    sendBundle(bundle) # defaults to "127.0.0.1", 9000

    dontListen()  # finally close the connection before exiting our program

