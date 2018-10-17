# This file is part of ctrl_notify.
#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (http://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
from ctypes import *
import ctypes.util
from inotifyEvent import _InotifyEvent, InotifyEvent

class Inotify(object):
    """An interface to the inotify_* Linux system calls.

    These are not exposed by the standard Python library, and do not
    exist in OS X.

    This library is intended to only be used on Linux systems.
    """

    def __init__(self):
        # initialize interfaces to the C library
        libcpath = ctypes.util.find_library("c")
        libc = cdll.LoadLibrary(libcpath)

        # inotify_init system call
        self.inotify_init = libc.inotify_init
        self.inotify_init.argtypes = []

        # inotify_add_watch system call
        self.inotify_add_watch = libc.inotify_add_watch
        self.inotify_add_watch.argtypes = [c_int, c_char_p, c_uint32]

        # inotify_rm_watch system call
        self.inotify_rm_watch = libc.inotify_rm_watch
        self.inotify_rm_watch.argtypes = [c_int, c_int]

        #
        # initialize the inotify interface
        #
        self.fd = self.inotify_init()
        self.filebuf = os.fdopen(self.fd)

        # dict of watches to paths
        self.paths = {}

        # dict of paths to watches
        self.watches = {}

    def readEvent(self, ignore=True):
        """Read the next inotify event. Blocks until event is received

        Parameters
        ----------
        ignore : `bool`, optional
            Should we read the event for IN_IGNORED on watch removal?

        Returns
        -------
        ievent : `InotifyEvent`
            The InotifyEvent that occured.
        """
        
        event = _InotifyEvent()
        val = self.filebuf.readinto(event)

        if ignore:
            while event.mask == InotifyEvent.IN_IGNORED:
                val = self.filebuf.readinto(event)

        ievent = None

        # if the event.length is greater than zero, there's a name associated
        # with this event, so it should be read.  If not, there's no name, so 
        # skip it.
        if event.length > 0:
            name = self.filebuf.read(event.length)
            path = self.paths[event.wd]
            ievent = InotifyEvent(event, os.path.join(path,name))
        else:
            ievent = InotifyEvent(event)
        return ievent

    def addWatch(self, path, mask):
        """Add a inotify watch request for a path.

        Parameters
        ----------
        path : `str`
            The path to watch.  Can be a file or directory.
        mask : `int`
            The `InotifyEvent` mask value to watch.
        """
        watch = self.inotify_add_watch(self.fd, path, mask)
        self.paths[watch] = path
        self.watches[path] = watch

    def rmWatch(self, path):
        """Add a inotify watch request for a path.

        Parameters
        ----------
        path : `str`
            The path to watch.  Can be a file or directory.
        """

        # TODO: remove only if path is in self.watches
        watch = self.watches.pop(path)
        ret = self.inotify_rm_watch(self.fd, watch)
        # TODO: remove only if watch is in self.paths
        p = self.paths.pop(watch)
        return ret

if __name__ == "__main__":

    note = Inotify()
    note.addWatch("/tmp/srp", InotifyEvent.IN_CREATE)
    note.addWatch("/tmp/srp2", InotifyEvent.IN_CREATE)
    event = note.readEvent()
    print(event.name)
    event = note.readEvent()
    print(event.name)
    print("removed /tmp/srp watcher")
    ret = note.rmWatch("/tmp/srp2")
    print(ret)
    event = note.readEvent()
    print(event.name)
