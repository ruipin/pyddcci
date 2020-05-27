# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from ctypes import windll, byref, sizeof, Structure, WinError
from ctypes.wintypes import RECT, DWORD, WCHAR

from . import struct_to_dict

from app.util import getLogger
log = getLogger(__name__)

#############
# CTypes Definitions/Types
CCHDEVICENAME = 32

class MONITORINFOEXW(Structure):
    _fields_ = [
        ('cbSize'   , DWORD                ),
        ('rcMonitor', RECT                 ),
        ('rcWork'   , RECT                 ),
        ('dwFlags'  , DWORD                ),
        ('szDevice' , WCHAR * CCHDEVICENAME)
    ]
    def to_dict(self):
        return struct_to_dict(self)
    def __repr__(self):
        return repr(self.to_dict())

    def is_primary(self):
        return self.dwFlags.value & 0x1  # MONITORINFOF_PRIMARY



###########
# Module implementation
def win32_get_monitor_info(handle):
    monitorInfo = MONITORINFOEXW()
    monitorInfo.cbSize = sizeof(MONITORINFOEXW)

    if not windll.user32.GetMonitorInfoW(handle, byref(monitorInfo)):
        raise WinError()

    return monitorInfo
