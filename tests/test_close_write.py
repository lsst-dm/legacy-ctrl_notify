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
        self.newFilePath = tempfile.mkdtemp()
        (fh, self.filename) = tempfile.mkstemp(dir=self.newFilePath)
        with os.fdopen(fh, "w") as tmp:
            tmp.write("test")

    def tearDown(self):
        shutil.rmtree(self.dirPath)
        self.note.close()

    def testCloseWrite(self):
        self.note.addWatch(self.dirPath, inotifyEvent.IN_CLOSE_WRITE)

        event = self.note.readEvent(timeout=3.0)

        self.assertIsNone(event)

        os.system(f"cp {self.filename} {self.dirPath}")

        event = self.note.readEvent(timeout=3.0)

        self.assertIsNotNone(event)
        self.assertEqual(event.mask, inotifyEvent.IN_CLOSE_WRITE)

        event = self.note.readEvent(timeout=3.0)
        self.assertIsNone(event)
