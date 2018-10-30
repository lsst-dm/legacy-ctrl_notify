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

from ctypes import c_int, c_char_p, c_uint32, cdll
import ctypes.util
from inotifyEvent import InotifyEvent

# initialize interfaces to the C library
_libcpath = ctypes.util.find_library("c")
_libc = cdll.LoadLibrary(_libcpath)

# inotify_init system call
inotify_init = _libc.inotify_init
inotify_init.argtypes = []

# inotify_add_watch system call
inotify_add_watch = _libc.inotify_add_watch
inotify_add_watch.argtypes = [c_int, c_char_p, c_uint32]

# inotify_rm_watch system call
inotify_rm_watch = _libc.inotify_rm_watch
inotify_rm_watch.argtypes = [c_int, c_int]

if __name__ == "__main__":

    fd = inotify_init()

    directory = r"/tmp/srp"
    wd = inotify_add_watch(fd, directory.encode('utf-8'), InotifyEvent.IN_CREATE)

    try:
        ret = inotify_rm_watch(fd, wd)
        if ret != 0:
            print('ret is 0')
    except Exception as error:
        print(error)

    try:
        ret = inotify_rm_watch(0, 12345)
        if ret == 0:
            print('ret is 0')
    except Exception as error:
        print(error)
