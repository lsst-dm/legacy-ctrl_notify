from ctypes import *
import ctypes.util
from const import *


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

        self.d = self.inotify_init()
        self.paths = {}

    def read_event(self):
        length = read(self.d, buf, EVENT_LEN)

    def add_watch(self, path, mask):
        watch = self.inotify_add_watch(self.d, path, mask)
        self.paths[path] = watch

    def rm_watch(self, path):
        watch = self.paths.pop(path)
        self.inotify_rm_watch(self.d, watch)

if __name__ == "__main__":

    note = Notify()
    note.add_watch("/tmp", IN_CREATE)
