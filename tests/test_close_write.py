#!/usr/bin/env python

#
# LSST Data Management System
#
# Copyright 2008-2018  AURA/LSST.
#
# This product includes software developed by the
# LSST Project (http://www.lsst.org/).
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
# You should have received a copy of the LSST License Statement and
# the GNU General Public License along with this program.  If not,
# see <https://www.lsstcorp.org/LegalNotices/>.
#

import lsst.ctrl.notify.notify as notify
import lsst.ctrl.notify.inotifyEvent as inotifyEvent
import lsst.utils.tests
import os
import shutil
import tempfile


def setup_module(module):
    lsst.utils.tests.init()


class CloseWriteTestCase(lsst.utils.tests.TestCase):
    """Test adding files to watcher"""

    def setUp(self):
        self.note = notify.Notify()
        self.dirPath = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.dirPath)
        self.note.close()

    def testCloseWrite(self):
        self.note.addWatch(self.dirPath, inotifyEvent.IN_CLOSE_WRITE)

        (fh, filename) = tempfile.mkstemp(dir=self.dirPath)
        with os.fdopen(fh, "w") as tmp:
            tmp.write("test")
            # file has been written to, but not yet closed, so check
            # to be sure we haven't gotten an event.
            event = self.note.readEvent(timeout=3.0)
            self.assertIsNone(event)

        # file is now closed, so event should be there
        event = self.note.readEvent(timeout=3.0)
        self.assertIsNotNone(event)
        self.assertEqual(event.mask, inotifyEvent.IN_CLOSE_WRITE)

        event = self.note.readEvent(timeout=3.0)
        self.assertIsNone(event)

    def testCloseWriteCopy(self):
        self.note.addWatch(self.dirPath, inotifyEvent.IN_CLOSE_WRITE)

        newFilePath = tempfile.mkdtemp()
        (fh, filename) = tempfile.mkstemp(dir=newFilePath)
        with os.fdopen(fh, "w") as tmp:
            tmp.write("test")

        event = self.note.readEvent(timeout=3.0)

        self.assertIsNone(event)

        os.system(f"cp {filename} {self.dirPath}")

        event = self.note.readEvent(timeout=3.0)

        self.assertIsNotNone(event)
        self.assertEqual(event.mask, inotifyEvent.IN_CLOSE_WRITE)

        event = self.note.readEvent(timeout=3.0)
        self.assertIsNone(event)
