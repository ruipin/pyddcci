# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

import ctypes
from ctypes import windll, byref, Structure, WinError, POINTER, WINFUNCTYPE
from ctypes.wintypes import BOOL, HMONITOR, HDC, RECT, DWORD, WCHAR, HANDLE, BYTE, LPARAM

from typing import Dict

from . import struct_asdict
from . import monitor_info

from app.util import getLogger
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
    def asdict(self):
        return struct_asdict(self)
    def __repr__(self):
        return repr(self.asdict())



############
# Classes that abstract away OS-specific Monitor behaviour/calls
class OsMonitorPhysicalHandle(object):
    def __init__(self, os_monitor):
        self.monitor = os_monitor
        self.handle  = None
        self.is_open = False  # self.handle may be None and still be valid

    # Opening/Closing
    def open(self):
        if self.is_open:
            return

        desired_physical_number = self.monitor.info.monitor.device.number
        desired_device_name = self.monitor.info.adapter.device.name

        # We need to find the hMonitor for the desired monitor using EnumDisplayMonitors
        virtual_handle = HMONITOR()

        def callback(hMonitor : int, hdcMonitor : HDC, lprcMonitor : 'ctypes._Pointer[RECT]', dwData : LPARAM) -> bool:
            info = None
            try:
                info = monitor_info.win32_get_monitor_info(hMonitor)
            except Exception as e:
                log.warning(f"Error calling win32_get_monitor_info({hMonitor}): {e}")
                return True

            if info.szDevice == desired_device_name:
                virtual_handle.value = hMonitor
                return False

            return True

        windll.user32.EnumDisplayMonitors(None, None, _MONITORENUMPROC(callback), None)

        if not virtual_handle.value:
            raise RuntimeError(f"Could not find a virtual handle for monitor {self.monitor}")

        # Get physical monitor count
        physical_count = DWORD()
        if not windll.dxva2.GetNumberOfPhysicalMonitorsFromHMONITOR(virtual_handle, byref(physical_count)):
            raise WinError()
        if physical_count.value <= desired_physical_number:
            if physical_count.value == 1:
                log.warning(f"Only 1 physical monitor found for {self.monitor} even though #{desired_physical_number} was requested. Assuming it is the desired one.")
                desired_physical_number = 0 # Assume we want the only physical monitor if only one is available
            else:
                raise RuntimeError(f"Could not find physical monitor at index {desired_physical_number} for {self.monitor}. Found {physical_count.value} physical monitors.")

        # Get physical monitor handles
        physical_array = (_PHYSICAL_MONITOR * physical_count.value)()
        if not windll.dxva2.GetPhysicalMonitorsFromHMONITOR(virtual_handle, physical_count, physical_array):
            raise WinError()

        found = False
        for i, physical in enumerate(physical_array):
            if i != desired_physical_number:
                self._close(physical.handle)
            elif found:
                raise RuntimeError(f"Found multiple physical monitors for {self.monitor} at index {i}, expected only one at index {desired_physical_number}")
            else:
                self.handle = physical.handle
                found = True

        if not found:
            raise RuntimeError(f"Could not find physical monitor at index {desired_physical_number} for {self.monitor}")

        self.is_open = True


    @staticmethod
    def _close(handle):
        if not windll.dxva2.DestroyPhysicalMonitor(handle):
            raise WinError()

    def close(self):
        if self.is_open:
            self._close(self.handle)
            self.handle = None
            self.is_open = False

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, typ, value, traceback):
        self.close()

    def __del__(self):
        self.close()


    # Functionality
    def query_vcp(self, command : int) -> Dict[str, int]:
        if not self.is_open:
            raise ValueError(f"{self} is not open. Did you forget to call open() or __enter__()?")

        codeType     = ctypes.c_uint32()
        currentValue = DWORD()
        maximumValue = DWORD()

        if not windll.dxva2.GetVCPFeatureAndVCPFeatureReply(HANDLE(self.handle), BYTE(command), byref(codeType), byref(currentValue), byref(maximumValue)):
            raise WinError()

        return {
            'command': int(command           ),
            'current': int(currentValue.value),
            'type'   : int(codeType.value    ),
            'maximum': int(maximumValue.value)
        }

    def set_vcp(self, command : int, value : int):
        if not self.is_open:
            raise ValueError(f"{self} is not open. Did you forget to call open() or __enter__()?")

        if not windll.dxva2.SetVCPFeature(HANDLE(self.handle), BYTE(command), DWORD(value)):
            raise WinError()


    def get_capabilities_string(self) -> str:
        if not self.is_open:
            raise ValueError(f"{self} is not open. Did you forget to call open() or __enter__()?")

        length = DWORD()
        if not windll.dxva2.GetCapabilitiesStringLength(self.handle, byref(length)):
            raise WinError()

        capabilities_string = (ctypes.c_char * length.value)()
        if not windll.dxva2.CapabilitiesRequestAndCapabilitiesReply(self.handle, capabilities_string, length):
            raise WinError()

        return capabilities_string.value.decode('ascii')
