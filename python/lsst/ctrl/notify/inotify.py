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
import select

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
        print("__init__ called")
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

    def add_watch(self, path, mask):
        """Add a inotify watch request for a path.

        Parameters
        ----------
        path : `str`
            The path to watch.  Can be a file or directory.
        mask : `int`
            The `InotifyEvent` mask value to watch.
        """
        watch = self.inotify_add_watch(self.fd, path, mask)
        return watch

    def rm_watch(self, wd):
        """Remove a inotify watch request for a path.

        Parameters
        ----------
        wd : `int`
            watch descriptor to remove.
        """

        ret = self.inotify_rm_watch(self.fd, wd)
        return ret


if __name__ == "__main__":

    note = Inotify()

    directory = "/tmp/srp"
    wd = note.add_watch(directory, InotifyEvent.IN_CREATE)

    try:
        ret = note.rm_watch(wd)
    except Exception as error:
        print(error)

    try:
        ret = note.rm_watch(12345)
    except Exception as error:
        print(error)
