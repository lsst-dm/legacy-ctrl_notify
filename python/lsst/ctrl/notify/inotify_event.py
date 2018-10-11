from ctypes import *

class _inotify_event(Structure):
    _fields_ = [('wd', c_int32),
                ('mask', c_uint32),
                ('cookie', c_uint32),
                ('length', c_uint32)]


class inotify_event(_inotify_event):
    def __init__(self, event=None, n=None):
        if event is not None:
            self.wd = event.wd
            self.mask = event.mask
            self.cookie = event.cookie
            self.length = event.length
        self.name = n
