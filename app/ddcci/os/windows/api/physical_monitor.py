# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from ctypes import windll, byref, Structure, WinError, POINTER, WINFUNCTYPE
from ctypes.wintypes import BOOL, HMONITOR, HDC, RECT, LPARAM, DWORD, WCHAR, HANDLE

from . import struct_to_dict

from . import getLogger
log = getLogger(__name__)


#############
# CTypes Definitions/Types
_MONITORENUMPROC = WINFUNCTYPE(BOOL, HMONITOR, HDC, POINTER(RECT), LPARAM)

PHYSICAL_MONITOR_DESCRIPTION_SIZE = 128
class _PHYSICAL_MONITOR(Structure):
    _fields_ = [
        ('handle', HANDLE),
        ('description', WCHAR * PHYSICAL_MONITOR_DESCRIPTION_SIZE)
    ]
    def to_dict(self):
        return struct_to_dict(self)
    def __repr__(self):
        return repr(self.to_dict())



############
# Classes that abstract away OS-specific Monitor behaviour/calls
class OsMonitorHandle(object):
    def __init__(self, os_monitor):
        self.monitor = os_monitor
        self.handle = None

    def open(self):
        return self.handle

    def close(self):
        if self.handle is not None:
            if not windll.dxva2.DestroyPhysicalMonitor(self.handle):
                raise WinError()

            self.handle = None

    def __enter__(self):
        return self.open()

    def __exit__(self, typ, value, traceback):
        self.close()

    def __del__(self):
        self.close()



###########
# Module implementation
def iter_monitors():
    """
    Iterates through the physical monitors reported by the Windows API.

    NOTE: The monitor handles are not closed! It is necessary to call 'close_monitor' when we're done with them.
    """

    def callback(hMonitor, hdcMonitor, lprcMonitor, dwData):
        print("cb: %s %s %s %s %s %s %s %s" % (hMonitor, type(hMonitor), hdcMonitor, type(hdcMonitor), lprcMonitor, type(lprcMonitor), dwData, type(dwData)))
        monitors.append(hMonitor)
        return True

    monitors = []
    if not windll.user32.EnumDisplayMonitors(None, None, _MONITORENUMPROC(callback), None):
        raise WinError()

    for monitor in monitors:
        # Get monitor count
        count = DWORD()
        if not windll.dxva2.GetNumberOfPhysicalMonitorsFromHMONITOR(monitor, byref(count)):
            raise WinError()

        print(count.value)
        # Get physical monitor handles
        physical_array = (_PHYSICAL_MONITOR * count.value)()
        if not windll.dxva2.GetPhysicalMonitorsFromHMONITOR(monitor, count, physical_array):
            raise WinError()

        for physical in physical_array:
            log.debug(repr(physical))
