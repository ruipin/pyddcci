# SPDX-License-Identifier: GPLv3-or-later
# Copyright © 2020 pyddcci Rui Pinheiro

from ctypes import windll, byref, sizeof, Structure
from ctypes.wintypes import DWORD, WCHAR

from . import struct_asdict

from app.util import getLogger
log = getLogger(__name__)


#############
# CTypes Definitions/Types

# DISPLAY_DEVICE_ACTIVE specifies whether a monitor is presented as being "on" by the respective GDI view.
# NOTE: Since Windows Vista EnumDisplayDevices will only enumerate monitors that can be presented as being "on."
DISPLAY_DEVICE_ACTIVE = 0x1

# Represents a pseudo device used to mirror application drawing for remoting or other purposes.
# An invisible pseudo monitor is associated with this device.
DISPLAY_DEVICE_MIRRORING_DRIVER = 0x8

# The device has more display modes than its output devices support.
DISPLAY_DEVICE_MODESPRUNED = 0x8000000

# The primary desktop is on the device.
# For a system with a single display card, this is always set.
# For a system with multiple display cards, only one device can have this set.
DISPLAY_DEVICE_PRIMARY_DEVICE = 0x4

# The device is removable
DISPLAY_DEVICE_REMOVABLE = 0x20

# The device is VGA compatible.
DISPLAY_DEVICE_VGA_COMPATIBLE = 0x10


class _DISPLAY_DEVICEW(Structure):
    _fields_ = [
        ('cb'          , DWORD      ),
        ('DeviceName'  , WCHAR * 32 ),
        ('DeviceString', WCHAR * 128),
        ('StateFlags'  , DWORD      ),
        ('DeviceID'    , WCHAR * 128),
        ('DeviceKey'   , WCHAR * 128)
    ]

    def asdict(self):
        return struct_asdict(self)
    def __repr__(self):
        return repr(self.asdict())

    @property
    def active(self):
        return (self.StateFlags & DISPLAY_DEVICE_ACTIVE) != 0
    @property
    def mirroring_driver(self):
        return (self.StateFlags & DISPLAY_DEVICE_MIRRORING_DRIVER) != 0
    @property
    def modes_pruned(self):
        return (self.StateFlags & DISPLAY_DEVICE_MODESPRUNED) != 0
    @property
    def primary(self):
        return (self.StateFlags & DISPLAY_DEVICE_PRIMARY_DEVICE) != 0
    @property
    def removable(self):
        return (self.StateFlags & DISPLAY_DEVICE_REMOVABLE) != 0
    @property
    def vga_compatible(self):
        return (self.StateFlags & DISPLAY_DEVICE_VGA_COMPATIBLE) != 0



############
# Module methods
EDD_GET_DEVICE_INTERFACE_NAME = 0x1

def win32_enum_display_devices_w(name, dev_num, flags=0x0):
    if name is None:
        deviceName = None
    elif isinstance(name, WCHAR):
        deviceName = name
    else:
        deviceName = (WCHAR * 32)()
        deviceName.value = name

    iDevNum = DWORD(dev_num)

    displayDevice = _DISPLAY_DEVICEW()
    displayDevice.cb = sizeof(_DISPLAY_DEVICEW)

    dwFlags = DWORD(flags)

    if not windll.user32.EnumDisplayDevicesW(None if deviceName is None else byref(deviceName), iDevNum, byref(displayDevice), dwFlags):
        return None

    return displayDevice

def enum_display_devices_by_name(dev_name):
    infos = []

    i = 0
    while True:
        monitor = win32_enum_display_devices_w(dev_name, i)
        if monitor is None:
            break

        infos.append(monitor)

        i += 1

    return infos


def enum_display_device(adapter_num, monitor_num):
    # Adapter details
    adapter = win32_enum_display_devices_w(None, adapter_num)
    if adapter is None:
        return None

    # Monitor details
    monitor = win32_enum_display_devices_w(adapter.DeviceName, monitor_num)
    if monitor is None:
        return None

    # Get monitor information
    return {'adapter': adapter, 'monitor': monitor}

def enum_display_devices():
    infos = []

    i = 0
    j = 0
    while True:
        while True:
            info = enum_display_device(i, j)

            if info is None:
                break

            infos.append(info)
            j += 1

        if j == 0:
            break

        j = 0
        i += 1

    return infos
