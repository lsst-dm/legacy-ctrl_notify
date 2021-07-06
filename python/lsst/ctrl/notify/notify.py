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
from lsst.ctrl.notify.inotify import inotify_init, inotify_add_watch, inotify_rm_watch
from lsst.ctrl.notify.inotifyEvent import _InotifyEvent, InotifyEvent


class Notify(object):
    def __init__(self):
        self.fd = inotify_init()
        self.filebuf = os.fdopen(self.fd, "rb")
        self.paths = {}
        self.watches = {}
        (self.r, self.w) = os.pipe()
        self.exitRead = os.fdopen(self.r)
        self.exitWrite = os.fdopen(self.w, 'w')

    def cancelReadEvent(self):
        self.exitWrite.write("cancel")
        self.exitWrite.flush()

    def readEvent(self, timeout=None):
        """Read the next inotify event. Blocks until event is received, unless
        timeout is specified.

        Parameters
        ----------
        timeout : `int`, optional
            seconds to wait for read to occur, defaults blocking until
            data is available

        Returns
        -------
        ievent : `InotifyEvent`
            The InotifyEvent that occured.
        """

        if timeout is None:
            rd, wr, ed = select.select([self.fd, self.exitRead], [], [])
        else:
            rd, wr, ed = select.select([self.fd, self.exitRead], [], [], timeout)

        # we're only reading, and one one inotify_init descriptor.  If
        # this comes back as zero, the timeout happened, and we return None.
        if len(rd) == 0:
            return None
        if (len(rd) == 1) and (rd[0] == self.exitRead):
            return None
        event = _InotifyEvent()

        # read the header of the event; you have to read in this much in
        # order to get the length of the name of the event.
        self.filebuf.readinto(event)

        ievent = None

        # if the event.length is greater than zero, there's a name associated
        # with this event, so it should be read.  If not, there's no name, so
        # skip it.
        if event.length > 0:
            # read the byte buffer and strip the trailing nulls
            # NOTE: this is required because if you don't, the decode will
            # will include the extra nulls are part of the string.  This
            # doesn't show up when you print, but it will cause an
            # assertEqual() to fail!
            name = self.filebuf.read(event.length).partition(b'\0')[0]
            # change this into a string
            name = name.decode('utf-8')
            path = self.paths[event.wd]
            ievent = InotifyEvent(event, os.path.join(path, name))
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
        watch = inotify_add_watch(self.fd, path.encode('utf-8'), mask)
        self.paths[watch] = path
        self.watches[path] = watch

    def rmWatch(self, path):
        """Remove a inotify watch request for a path.

        Parameters
        ----------
        path : `str`
            The path to watch.  Can be a file or directory.
        """

        watch = self.watches.pop(path)
        self.paths.pop(watch)
        ret = inotify_rm_watch(self.fd, watch)
        return ret

    def close(self):
        self.exitRead.close()
        self.exitWrite.close()
        self.filebuf.close()
