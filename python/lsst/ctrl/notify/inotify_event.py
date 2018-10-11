from ctypes import *

class _inotify_event(Structure):
    _fields_ = [('wd', c_int32),
                ('mask', c_uint32),
                ('cookie', c_uint32),
                ('length', c_uint32)]


class inotify_event(_inotify_event):
    name = None
    def __init__(self, event=None):
        if event is not None:
            self.__dict__.update(event.__dict__) 

