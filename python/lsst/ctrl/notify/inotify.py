import os
from ctypes import *
import ctypes.util
from inotifyEvent import _InotifyEvent, InotifyEvent


class Inotify(object):

    def __init__(self):
        libcpath = ctypes.util.find_library("c")
        libc = cdll.LoadLibrary(libcpath)

        self.inotify_init = libc.inotify_init
        self.inotify_init.argtypes = []

        self.inotify_add_watch = libc.inotify_add_watch
        self.inotify_add_watch.argtypes = [c_int, c_char_p, c_uint32]

        self.inotify_rm_watch = libc.inotify_rm_watch
        self.inotify_rm_watch.argtypes = [c_int, c_int]

        self.fd = self.inotify_init()
        self.filebuf = os.fdopen(self.fd)
        self.paths = {}
        self.watches = {}

    def readEvent(self):
        event = _InotifyEvent()
        val = self.filebuf.readinto(event)
        name = self.filebuf.read(event.length)
        print("readEvent: name =",name)
        print("readEvent: wd =",event.wd)
        print("readEvent: mask =",event.mask)
        path = self.paths[event.wd]
        ievent = InotifyEvent(event, os.path.join(path,name))
        return ievent

    def addWatch(self, path, mask):
        watch = self.inotify_add_watch(self.fd, path, mask)
        self.paths[watch] = path
        self.watches[path] = watch

    def rmWatch(self, path, ignore=True):
        watch = self.watches.pop(path)
        ret = self.inotify_rm_watch(self.fd, watch)
        print("ignore")
        event = self.readEvent()
        print("ignore done")
        p = self.paths.pop(watch)
        print("removing ",watch,p)
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
