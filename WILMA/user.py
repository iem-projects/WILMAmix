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
logging = logging_.getLogger('WILMA.user')

import os, os.path

import pwd, grp


def getUID(user=None):
    if user is None:
        return os.getuid()
    try:
        try:
            p=pwd.getpwnam(user)
            return p.pw_uid
        except KeyError:
            pass
        try:
            uid=int(user)
            u=pwd.getpwuid(uid)
            return uid
        except ValueError, KeyError:
            logging.exception("invalid user ID '%(user)s'" % locals())
    except:
        logging.exception("invalid user name '%(user)s'" % locals())
    return os.getuid()

def getGID(group=None):
    if group is None:
        return os.getgid()
    try:
        try:
            g=grp.getgrnam(group)
            return g.gr_gid
        except KeyError:
            pass
        try:
            gid=int(group)
            g=grp.getgrgid(gid)
            return gid
        except ValueError, KeyError:
            logging.exception("invalid group ID '%(group)s'" % locals())

    except:
        logging.exception("invalid group name '%(group)s'" % locals())
    return os.getgid()

getpass=None
def getUser(user=None):
    global getpass
    try:
        uid=getUID(user)
        u=pwd.getpwuid(uid).pw_name
    except KeyError:
        if getpass is None:
            import getpass
        u=getpass.getuser()
    return u

def getHome(user=None):
    if user is None:
        return os.path.expanduser("~")
    if os.path.isdir(user):
        return user
    return pwd.getpwuid(getUser(user)).pw_dir
        

####################################################


if __name__ == '__main__':
    import sys
    print("default: UID:%d\tGID=%d\tHOME=%s" % (getUser(), getGroup(), getHome()))
    for s in sys.argv[1:]:
        uid=getUser(s)
        gid=getGroup(s)
        home=getHome(s)
        print("'%(s)s' -> UID:%(uid)d\tGID:%(gid)d\tHOME:%(home)s" % locals())

