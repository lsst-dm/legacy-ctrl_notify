import os
from ctypes import *
import ctypes.util
from inotifyEvent import _InotifyEvent, InotifyEvent


class Inotify(object):

    # Supported events suitable for MASK parameter of INOTIFY_ADD_WATCH.
    IN_ACCESS        = 0x00000001 # File was accessed.
    IN_MODIFY        = 0x00000002 # File was modified.
    IN_ATTRIB        = 0x00000004 # Metadata changed.
    IN_CLOSE_WRITE   = 0x00000008 # Writtable file was closed.
    IN_CLOSE_NOWRITE = 0x00000010 # Unwrittable file closed.
    IN_CLOSE         = (IN_CLOSE_WRITE | IN_CLOSE_NOWRITE) # Close.
    IN_OPEN          = 0x00000020 # File was opened.
    IN_MOVED_FROM    = 0x00000040 # File was moved from X.
    IN_MOVED_TO      = 0x00000080 # File was moved to Y.
    IN_MOVE          = (IN_MOVED_FROM | IN_MOVED_TO) # Moves.
    IN_CREATE        = 0x00000100 # Subfile was created.
    IN_DELETE        = 0x00000200 # Subfile was deleted.
    IN_DELETE_SELF   = 0x00000400 # Self was deleted.
    IN_MOVE_SELF     = 0x00000800 # Self was moved.
    
    IN_ALL_EVENTS    = (IN_ACCESS | IN_MODIFY | IN_ATTRIB | IN_CLOSE_WRITE | \
                        IN_CLOSE_NOWRITE | IN_OPEN | IN_MOVED_FROM | IN_MOVED_TO | \
                        IN_CREATE | IN_DELETE | IN_DELETE_SELF | IN_MOVE_SELF)

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

    def readEvent(self):
        event = _InotifyEvent()
        val = self.filebuf.readinto(event)
        name = self.filebuf.read(event.length)
        path = self.paths[event.wd]
        ievent = InotifyEvent(event, os.path.join(path,name))
        return ievent

    def addWatch(self, path, mask):
        watch = self.inotify_add_watch(self.fd, path, mask)
        self.paths[watch] = path

    def rmWatch(self, path):
        watch = self.paths.pop(path)
        self.inotify_rm_watch(self.fd, watch)

if __name__ == "__main__":

    note = Inotify()
    note.addWatch("/tmp/srp", Inotify.IN_CREATE)
    note.addWatch("/tmp/srp2", Inotify.IN_CREATE)
    event = note.readEvent()
    print(event.name)
    event = note.readEvent()
    print(event.name)
