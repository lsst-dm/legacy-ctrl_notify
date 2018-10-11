import os
from ctypes import *
import ctypes.util
from const import *
from inotify_event import _inotify_event, inotify_event


class Notify(object):

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

    def read_event(self):
        event = _inotify_event()
        val = self.filebuf.readinto(event)
        print("done")
        name = self.filebuf.read(event.length)
        print(name, event.length)
        ievent = inotify_event(event, name)
        return ievent

    def add_watch(self, path, mask):
        watch = self.inotify_add_watch(self.fd, path, mask)
        self.paths[path] = watch

    def rm_watch(self, path):
        watch = self.paths.pop(path)
        self.inotify_rm_watch(self.fd, watch)

if __name__ == "__main__":

    note = Notify()
    note.add_watch("/tmp", IN_CREATE)
    event = note.read_event()
    print(event.wd)
    print(event.mask)
    print(event.cookie)
    print(event.length)
    print(event.name)
