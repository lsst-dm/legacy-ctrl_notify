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

import unittest
import lsst.ctrl.notify as notify
import lsst.utils.tests
import tempfile
import shutil

def setup_module(module):
    lsst.utils.tests.init()

class AddWatchTestCase(lsst.utils.tests.TestCase):
    """Test adding files to watcher"""

    def testCreate(self):
        direct = tempfile.mkdtemp()

        note = notify.iNotify()
        note.addWatch(path, IN_CREATE)

        (fh, filename) = tempfile.mkstemp(dir=path)
        event = note.readEvent()

        self.assertEqual(event.mask, notify.InotifyEvent.IN_CREATE)
        self.assertEqual(event.name, filename)

        shutil.rmtree(direct)

class Test1MemoryTester(lsst.utils.tests.MemoryTestCase):
    pass

if __name__ == "__main__":
    lsst.utils.tests.init()
    unittest.main()
