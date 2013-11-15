#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Open SoundControl for Python
# Copyright (C) 2002 Daniel Holth, Clinton McChesney
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# For questions regarding this module contact
# Daniel Holth <dholth@stetson.edu> or visit
# http://www.stetson.edu/~ProctoLogic/
#
# Changelog:
# 15 Nov. 2001:
#   Removed dependency on Python 2.0 features.
#   - dwh
# 13 Feb. 2002:
#   Added a generic callback handler.
#   - dwh
import logging as logging_
logging = logging_.getLogger('OSC')

import socket
import struct
import math
import sys
import string
import pprint
import re

def hexDump(bytes):
    """Useful utility; prints the string in hexadecimal"""
    for i in range(len(bytes)):
        sys.stdout.write("%2x " % (ord(bytes[i])))
        if (i+1) % 8 == 0:
            print repr(bytes[i-7:i+1])

    if(len(bytes) % 8 != 0):
        print string.rjust("", 11), repr(bytes[i-len(bytes)%8:i+1])

class OSCException(Exception):
    pass

class OSCMessage(object):
    """Builds typetagged OSC messages."""
    def __init__(self):
        self.address  = ""
        self.typetags = ","
        self.message  = ""

    def setAddress(self, address):
        self.address = address

    def setMessage(self, message):
        self.message = message

    def setTypetags(self, typetags):
        self.typetags = typetags

    def clear(self):
        self.address  = ""
        self.clearData()

    def clearData(self):
        self.typetags = ","
        self.message  = ""

    def append(self, argument, typehint = None):
        """Appends data to the message,
        updating the typetags based on
        the argument's type.
        If the argument is a blob (counted string)
        pass in 'b' as typehint."""

        if typehint == 'b':
            binary = OSCBlob(argument)
        else:
            binary = OSCArgument(argument)

        self.typetags = self.typetags + binary[0]
        self.rawAppend(binary[1])

    def rawAppend(self, data):
        """Appends raw data to the message.  Use append()."""
        self.message = self.message + data

    def getBinary(self):
        """Returns the binary message (so far) with typetags."""
        address  = OSCArgument(self.address)[1]
        typetags = OSCArgument(self.typetags)[1]
        return address + typetags + self.message

    def __repr__(self):
        return self.getBinary()

def readString(data):
    length   = string.find(data,"\0")
    nextData = int(math.ceil((length+1) / 4.0) * 4)
    return (data[0:length], data[nextData:])

def readBlob(data):
    length   = struct.unpack(">i", data[0:4])[0]
    nextData = int(math.ceil((length) / 4.0) * 4) + 4
    return (data[4:length+4], data[nextData:])


def readInt(data):
    integer = struct.unpack(">i", data[0:4])[0]
    rest    = data[4:]
    return (integer, rest)

def readLong(data):
    """Tries to interpret the next 8 bytes of the data
    as a 64-bit signed integer."""
    big = struct.unpack(">q", data[0:8])[0]
    rest = data[8:]
    return (big, rest)

def readULong(data):
    """Tries to interpret the next 8 bytes of the data
    as a 64-bit unsigned integer."""
    big = struct.unpack(">Q", data[0:8])
    rest = data[8:]
    return (big, rest)

def readDouble(data):
    """Tries to interpret the next 8 bytes of the data
    as a 64-bit double float."""
    floater = struct.unpack(">d", data[0:8])
    big = float(floater[0])
    rest = data[8:]
    return (big, rest)

def readFloat(data):
    return (struct.unpack(">f", data[0:4])[0], data[4:])

def readChar(data):
    (i,r) = readInt(data)
    return (chr(i & 0xff), r)

def readMIDI(data):
    return (struct.unpack('>bbbb', data[0:4])[0], data[4:])

def readTrue(data):
    return (True, data)

def readFalse(data):
    return (False, data)

def readNil(data):
    return (None, data)

def readInf(data):
    return (float('Inf'), data)

def OSCBlob(next):
    """Convert a string into an OSC Blob,
    returning a (typetag, data) tuple."""
    if type(next) == type(""):
        length = len(next)
        padded = math.ceil((len(next)) / 4.0) * 4
        binary = struct.pack(">i%ds" % (padded), length, next)
        tag    = 'b'
    else:
        tag    = ''
        binary = ''

    return (tag, binary)


def OSCArgument(next):
    """Convert some Python types to their
    OSC binary representations, returning a
    (typetag, data) tuple."""

    typ=type(next)

    ## int32 types are a bit problematic, as python reports
    ## unsigned ints (that exceed the range of signed ints)
    ## as 'int', but struct('>i') cannot handle these
    if (typ == int) and (next>=0x7fffffff or next<-0x80000000):
        typ=type(long(0))

    if str     == typ:
        OSCstringLength = math.ceil((len(next)+1) / 4.0) * 4
        binary  = struct.pack('>%ds' % (OSCstringLength), next)
        tag = 's'
    elif float == typ:
        binary  = struct.pack('>f', next)
        tag = 'f'
    elif int   == typ:
        binary  = struct.pack('>i', next)
        tag = 'i'
    elif long  == typ:
        binary  = struct.pack('>q', next)
        tag = 'h'
    elif bool  == typ:
        binary = ''
        if next is True:
            tag = 'T'
        else:
            tag = 'F'
    elif next is None:
        binary = ''
        tag = 'N'
    else:
        binary  = ''
        tag = 'N' ## better than nothing...

    return (tag, binary)


def parseArgs(args):
    """Given a list of strings, produces a list
    where those strings have been parsed (where
    possible) as floats or integers."""
    parsed = []
    for arg in args:
        #print arg
        arg = arg.strip()
        interpretation = None
        try:
            interpretation = float(arg)
            if string.find(arg, ".") == -1:
                interpretation = int(interpretation)
        except:
            # Oh - it was a string.
            interpretation = arg
            pass
        parsed.append(interpretation)
    return parsed



def decodeOSC(data):
##    i + 32bit integer
##    h + 64bit integer
##    f + 32bit floating point number
##    d + 64bit (double) floating point number
##    s + string
##    S + symbol
##    c - char /* an ascii character, sent as 32 bits */
##    m - 4 byte midi packet (8 digits hexadecimal) /* port id, status byte, data1, data2 */
##    T + TRUE
##    F + FALSE
##    N + NIL
##    I + INFINITUM

    """Converts a typetagged OSC message to a Python list."""
    table = { 'i' : readInt, 'f' : readFloat, 's' : readString, 'b' : readBlob, 'd' : readDouble,
              'h' : readLong,
              'S' : readString,
              'c' : readChar,
              'm' : readMIDI,
              'T' : readTrue, 'F': readFalse, 'N': readNil, 'I': readInf
              }
    decoded = []
    address,  rest = readString(data)
    typetags = ''

    if address == '#bundle':
        time, rest = readULong(rest)
        decoded.append(address)
        decoded.append(time)
        while len(rest)>0:
            length, rest = readInt(rest)
            decoded.append(decodeOSC(rest[:length]))
            rest = rest[length:]

    elif len(rest) > 0:
        typetags, rest = readString(rest)
        decoded.append(address)
        decoded.append(typetags)
        if len(typetags)>0 and typetags[0] == ',':
            for tag in typetags[1:]:
                try:
                    value, rest = table[tag](rest)
                except struct.error:
                    logging.exception("wrong number of bytes (%d) for type '%s'" % (len(rest), tag))
                    return decoded
                decoded.append(value)
        else:
            logging.warn( "Oops, typetag lacks the magic ','")

    return decoded


class CallbackManager(object):
    """This utility class maps OSC addresses to callables.

    The CallbackManager calls its callbacks with a list
    of decoded OSC arguments, including the address and
    the typetags as the first two arguments."""

    def __init__(self, prefix=None, verbose=False):
        self.verbose=verbose
        self.callbacks = {}
        self.subtreecallbacks = []
        self.bundlecallback = None
        self.bundledepth    = 0
        self.prefix=None
        if prefix is not None:
            self.prefix=prefix.split('/')[1:]
        self.removeAll()

    def handle(self, data, source = None):
        """Given OSC data, tries to call the callback with the
        right address."""
        decoded = decodeOSC(data)
        self.dispatch(decoded, source)

    def dispatch(self, message, source = None):
        """Sends decoded OSC data to an appropriate callback"""
        logging.log(1, "dispatching: '%s' from %s" % (str(message),str(source)))
        try:
            address=message[0]
        except IndexError, e:
            logging.exception( "got malformed OSC message: '%s'" % str( message))
            return

        if type(address) == str :
            if '#bundle' == address:
                self.unbundler(message, source)
                return
            # got a single message
            found=False
            cb=None
            subtree=address.split('/')[1:]

            # first check whether it matches our prefix (if any)
            if self.prefix is not None:
                if not self.matchSubtree(subtree, self.prefix):
                    return # prefix match failed
                subtree=subtree[len(self.prefix):]
                address='/'+'/'.join(subtree)

            ## try direct matching
            if self.isWildcard(address):
                for a in self.matchWildcards(address, self.callbacks.keys()):
                    cb=None
                    try:
                        cb=self.callbacks[a]
                    except KeyError, e:
                        cb=None
                    if cb is not None:
                        cb([a, message[0]], message[1], message[2:], source)
                        found=True
            else:
                try:
                    cb=self.callbacks[address]
                except KeyError, e:
                    cb=None
                if cb is not None:
                    cb([address, message[0]], message[1], message[2:], source)
                    found=True

            ## try subtree matching
            subtreefound=False
            for st, cb in self.subtreecallbacks:
                if self.matchSubtree(subtree, st):
                    ## the rest address, without the subtree
                    staddr='/'+'/'.join(subtree[len(st):])
                    cb([staddr, message[0]], message[1], message[2:], source)
                    found=True

            # address not found
            if not found:
                if self.catchall is not None:
                    self.catchall([address, message[0]], message[1], message[2:], source)
                else:
                    logging.warn( '\tOSC-address %s not found in callback manager' % address)
                    logging.info(pprint.pformat(message))

        elif type(address) == list :
            # smells like nested messages
            for msg in message :
                self.dispatch(msg, source)

        return

    def add(self, callback, name):
        """
        Adds a callback to our set of callbacks,
        or removes the callback with name if callback is None.
        wildcard patterns are NOT supported.
        """
        if (callback is not None) and not callable(callback):
            raise OSCException("callback needs to be callable: "+str(callback))
        if name is None:
            self.catchall = callback
        elif type(name) is str:
            if '#bundle' == name:
                self.bundlecallback=callback
                return
            if not name.startswith('/'):
                raise OSCException("name is not a valid OSC-address: "+str(name))

            if callback == None:
                if name.endswith('/'):
                    stree=name.split('/')[1:-1]
                    newsubtrees = [ x for x in self.subtreecallbacks if x[0] != stree]
                    self.subtreecallbacks=newsubtrees
                else:
                    try:
                        del self.callbacks[name]
                    except KeyError:
                        pass
            else:
                if name.endswith('/'):
                    self.subtreecallbacks+=[[name.split('/')[1:-1], callback]]
                else:
                    self.callbacks[name] = callback
        else:
            raise OSCException("name needs to be a string: "+str(name))

    def remove(self, name):
        """Removes a callback from our callback set"""
        self.add(None, name)
    def removeAll(self):
        """Removes all callbacks"""
        self.callbacks={}
        self.subtreecallbacks = []
        self.catchall = None
        self.bundlecallback=None

    def unbundler(self, messages, source):
        """Dispatch the messages in a decoded bundle."""
        # first two elements are #bundle and the time tag, rest are messages.
        timetag=messages[1]
        bc = self.bundlecallback
        depth = self.bundledepth
        self.bundledepth+=1
        if bc is not None:
            bc(timetag, True, depth, source)
        for message in messages[2:]:
            self.dispatch(message, source)
        if bc is not None:
            bc(timetag, False, depth, source)
        self.bundledepth-=1

## pattern matching code
# Copyright © 2009 Alexandre Quessy, Arjan Scherpenisse
# Copyright © 2013, IOhannes m zmölnig, IEM

    @staticmethod
    def isWildcard(name):
        """
        Given a name, returns whether it contains wildcard characters.
        """
        wildcardChars = set("*?[]{}")
        return len(set(name).intersection(wildcardChars)) > 0

    @staticmethod
    def matchWildcards(pattern, keys):
        """
        returns a list of keys that match the given pattern.
        code mainly taken from from python-txosc
        """
        if pattern == "*":
            return keys
        # OSC-patterns -> regular expressions
        rpattern = ('^' +
                    (pattern
                    .replace("*", ".*")
                    .replace("?", ".?")
                    .replace("[!", "[^")
                    .replace("(", "\(")
                    .replace(")", "\)")
                    .replace("|", "\|")
                    .replace("{", "(")
                    .replace("}", ")")
                    .replace(",", "|")
                    )+'$')
        try:
            r = re.compile(rpattern)
        except:
            raise OSCException("invalid character in pattern '"+pattern+"' -> "+rpattern)
        try:
            return filter(r.match, keys)
        except TypeError as e:
            logging.warn("error matching %s" % str( (pattern, keys) ))
            raise OSCException(str(e))

    @staticmethod
    def matchSubtree(pattern, key):
        """
        like matchWildcards, but pattern&keys are decomposed into elements,
        and matches even if pattern is longer than key
        """
        if len(key)>len(pattern): ## can never match, since the registered address is longer than the address we received
            return False

        for a,b in zip(pattern, key):
            if CallbackManager.isWildcard(a):
                if 0 == len(CallbackManager.matchWildcards(a, [b])):
                    return False
            else:
                if a != b:
                    return False

        return True




######################################################################

if __name__ == "__main__":
    hexDump("Welcome to the OSC testing program.")
    print
    message = OSCMessage()
    message.setAddress("/foo/play")
    message.append(44)
    message.append(11)
    message.append(4.5)
    message.append("the white cliffs of dover")
    hexDump(message.getBinary())

    print "Making and unmaking a message.."

    strings = OSCMessage()
    strings.append("Mary had a little lamb")
    strings.append("its fleece was white as snow")
    strings.append("and everywhere that Mary went,")
    strings.append("the lamb was sure to go.")
    strings.append(14.5)
    strings.append(14.5)
    strings.append(-400)

    raw  = strings.getBinary()

    hexDump(raw)

    print "Retrieving arguments..."
    data = raw
    for i in range(6):
        text, data = readString(data)
        print text

    number, data = readFloat(data)
    print number

    number, data = readFloat(data)
    print number

    number, data = readInt(data)
    print number

    hexDump(raw)
    print decodeOSC(raw)
    print decodeOSC(message.getBinary())

    print "Testing Blob types."

    blob = OSCMessage()
    blob.append("","b")
    blob.append("b","b")
    blob.append("bl","b")
    blob.append("blo","b")
    blob.append("blob","b")
    blob.append("blobs","b")
    blob.append(42)

    hexDump(blob.getBinary())

    print decodeOSC(blob.getBinary())

    def printingCallback(*stuff):
        sys.stdout.write("\tPRINT   Got: ")
        for i in stuff:
            sys.stdout.write("\t"+str(i) + " ")
        sys.stdout.write("\n")
    def subtreeCallback(*stuff):
        sys.stdout.write("\tSUBTREE Got: ")
        for i in stuff:
            sys.stdout.write("\t"+str(i) + " ")
        sys.stdout.write("\n")
    def bundleCallback(timetag, starting, depth, source):
        print "\t#bundle", (timetag, starting, depth, source)

    print "Testing the callback manager."

    c = CallbackManager()
    c.add(printingCallback, "/print")
    c.add(subtreeCallback, "/foo/")

    c.add(printingCallback, "/path/print")
    c.add(subtreeCallback, "/path/subpath/")
    c.add(bundleCallback, "#bundle")

    print "testing message: /foo/play"
    c.handle(message.getBinary())

    message.setAddress("/print")
    print "testing message: /print"
    c.handle(message.getBinary())

    print1 = OSCMessage()
    print1.setAddress("/pr?nt")
    print1.append("Hey man, patterns match.")
    print1.append(42)

    print "testing pattern-matching: /pr?nt"
    c.handle(print1.getBinary(), "matcher")

    print1 = OSCMessage()
    print1.setAddress("/print")
    print1.append("Hey man, that's cool.")
    print1.append(42)
    print1.append(3.1415926)

    print "testing single message: /print"
    c.handle(print1.getBinary(), "bar")

    bundle = OSCMessage()
    bundle.setAddress("")
    bundle.append("#bundle")
    bundle.append(0)
    bundle.append(0)
    bundle.append(print1.getBinary(), 'b')
    bundle.append(print1.getBinary(), 'b')

    bundlebinary = bundle.message

    print "sending a bundle to the callback manager"
    c.handle(bundlebinary, source="foo")

    msg = OSCMessage()
    msg.setAddress("/foo/bar/baz")
    msg.append(666)
    print "sending a message to the callback manager (should match subtree: /foo/)"
    c.handle(msg.getBinary())
    msg = OSCMessage()
    print "sending a message to the callback manager (should patternmatch subtree: /foo/)"
    msg.setAddress("/f*o/schu")
    msg.append(3996747840)
    c.handle(msg.getBinary())
    print "sending a message to the callback manager (should patternmatch subtree: /foo/)"
    msg.setAddress("/f*o/b?z")
    msg.append(777)
    c.handle(msg.getBinary())

    msg = OSCMessage()
    print "sending a message to the callback manager (should NOT patternmatch subtree)"
    msg.setAddress("/f*u/didoo")
    msg.append(9)
    c.handle(msg.getBinary())

    msg = OSCMessage()
    msg.setAddress("/path/print")
    msg.append("PRINT")
    print "sending a message to the callback manager (should NOT match subtree, but print)"
    c.handle(msg.getBinary())
    msg = OSCMessage()
    msg.setAddress("/path/subpath/file")
    msg.append("SUBTREE")
    print "sending a message to the callback manager (should NOT print, but match subtree: /path/subpath/)"
    c.handle(msg.getBinary())

    print "removing callbacks"
    print "old callbacks", c.callbacks
    c.add(None, "/print")
    c.remove('/path/print')
    c.add(None, "/run")
    print "new callbacks", c.callbacks
    print "old subtreecallbacks", c.subtreecallbacks
    c.remove("/print")
    c.remove("/foo/")
    c.remove("/kug/")
    c.remove("/path/subpath/")
    print "new subtreecallbacks", c.subtreecallbacks
    c.removeAll()
