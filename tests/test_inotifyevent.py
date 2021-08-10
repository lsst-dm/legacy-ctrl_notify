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

import asynctest
import lsst.ctrl.notify.notify as notify
import lsst.ctrl.notify.inotifyEvent as inotifyEvent
import lsst.utils.tests
import os
import tempfile
import shutil


def setup_module(module):
    lsst.utils.tests.init()


class InotifyEventTestCase(asynctest.TestCase):
    """Test InotifyEvent"""

    def setUp(self):
        self.note = notify.Notify()
        self.dirPath = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.dirPath)
        self.note.close()

    async def testInotifyEvent(self):
        self.note.addWatch(self.dirPath, inotifyEvent.IN_CREATE)

        (fh, filename) = tempfile.mkstemp(dir=self.dirPath)
        event = await self.note.readEvent(0)

        self.assertEqual(event.mask, inotifyEvent.IN_CREATE)
        self.assertEqual(event.name, filename)
        self.assertNotEqual(event.cookie, -1)
        self.assertNotEqual(event.length, -1)

    async def testSubdirectory(self):
        self.note.addWatch(self.dirPath, inotifyEvent.IN_CREATE)

        path1 = os.path.join(self.dirPath, str(os.getpid()))
        os.makedirs(path1)
        event = await self.note.readEvent(0)
        self.assertEqual(event.name, path1)

        (fh, filename) = tempfile.mkstemp(dir=path1)
        event = await self.note.readEvent(0)
        self.assertIsNone(event)

        self.note.addWatch(path1, inotifyEvent.IN_CREATE)

        (fh, filename) = tempfile.mkstemp(dir=path1)
        event = await self.note.readEvent(0)
        self.assertEqual(event.name, filename)

    async def testWritingClosed(self):
        self.note.addWatch(self.dirPath, inotifyEvent.IN_CLOSE_WRITE)

        path = os.path.join(self.dirPath, str(os.getpid()))
        f = open(path, "w")
        f.write("Hi there")
        event = await self.note.readEvent(0)
        self.assertIsNone(event)
        f.close()
        event = await self.note.readEvent(0)
        self.assertEqual(event.name, path)
        self.assertNotEqual(event.cookie, -1)
        self.assertNotEqual(event.length, -1)

    def testNullEvent(self):
        event = inotifyEvent.InotifyEvent()
        self.assertEqual(event.wd, -1)
        self.assertEqual(event.mask, -1)
        self.assertEqual(event.cookie, -1)
        self.assertEqual(event.length, -1)
