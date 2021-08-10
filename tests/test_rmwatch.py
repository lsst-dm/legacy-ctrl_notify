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
import tempfile
import shutil


def setup_module(module):
    lsst.utils.tests.init()


class RemoveWatchTestCase(asynctest.TestCase):
    """Test removing watches"""

    def setUp(self):
        self.note = notify.Notify()
        self.dirPath = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.dirPath)

    async def testRemoveValidWatch(self):
        self.note.addWatch(self.dirPath, inotifyEvent.IN_CREATE)

        event = await self.note.readEvent(timeout=5.0)
        self.assertIsNone(event)

        self.note.rmWatch(self.dirPath)
        event = await self.note.readEvent(timeout=5.0)

        self.assertIsNotNone(event)

        self.assertEqual(event.mask, inotifyEvent.IN_IGNORED)

        with self.assertRaises(KeyError):
            self.note.rmWatch("/notapath")
        self.note.close()

    def testRemoveInValidWatch(self):
        self.note.addWatch(self.dirPath, inotifyEvent.IN_CREATE)
        self.note.close()

        self.note.fd = -1
        ret = self.note.rmWatch(self.dirPath)
        self.assertEqual(ret, -1)
