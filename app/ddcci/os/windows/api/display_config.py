# SPDX-License-Identifier: GPLv3-or-later
# Copyright © 2020 pyddcci Rui Pinheiro

import ctypes
from ctypes import windll, byref, sizeof, Structure, Union, WinError, GetLastError
from ctypes.wintypes import BOOL, DWORD, WCHAR, LONG, POINTL, RECTL

from . import struct_asdict
from .device_path import DevicePath

from dataclasses import dataclass
from typing import Dict, Any


#############
# CTypes Definitions/Types
CCHDEVICENAME = 32

class LUID(ctypes.Structure):
    _fields_ = [
        ('LowPart' , DWORD),
        ('HighPart', LONG )
    ]
    def asdict(self):
        return struct_asdict(self)
    def __repr__(self):
        return repr(self.asdict())

class DISPLAYCONFIG_PATH_SOURCE_INFO(Structure):
    _fields_ = [
        ('adapterId'  , LUID           ),
        ('id'         , ctypes.c_uint32),
        ('modeInfoIdx', ctypes.c_uint32),  # union { uint16 cloneGroupId; uint16 sourceModeInfoIdx }
        ('statusFlags', ctypes.c_uint32),
    ]
    def asdict(self):
        return struct_asdict(self)
    def __repr__(self):
        return repr(self.asdict())

class DISPLAYCONFIG_RATIONAL(Structure):
    _fields_ = [
        ('Numerator'  , ctypes.c_uint32),
        ('Denominator', ctypes.c_uint32)
    ]
    def asdict(self):
        return struct_asdict(self)
    def __repr__(self):
        return repr(self.asdict())

class DISPLAYCONFIG_PATH_TARGET_INFO(Structure):
    _fields_ = [
        ('adapterId'       , LUID                  ),
        ('id'              , ctypes.c_uint32       ),
        ('modeInfoIdx'     , ctypes.c_uint32       ),  # union { uint16 desktopModeInfoIdx; uint16 targetModeInfoIdx }
        ('outputTechnology', ctypes.c_uint32       ),  # enum DISPLAYCONFIG_VIDEO_OUTPUT_TECHNOLOGY
        ('rotation'        , ctypes.c_uint32       ),  # enum DISPLAYCONFIG_ROTATION
        ('scaling'         , ctypes.c_uint32       ),  # enum DISPLAYCONFIG_SCALING
        ('refreshRate'     , DISPLAYCONFIG_RATIONAL),  # enum DISPLAYCONFIG_RATIONAL
        ('scanLineOrdering', ctypes.c_uint32       ),  # enum DISPLAYCONFIG_SCANLINE_ORDERING
        ('targetAvailable' , BOOL                  ),
        ('statusFlags'     , ctypes.c_uint32       )
    ]
    def asdict(self):
        return struct_asdict(self)
    def __repr__(self):
        return repr(self.asdict())

class DISPLAYCONFIG_PATH_INFO(Structure):
    _fields_ = [
        ('sourceInfo', DISPLAYCONFIG_PATH_SOURCE_INFO),
        ('targetInfo', DISPLAYCONFIG_PATH_TARGET_INFO),
        ('flags'     , ctypes.c_uint32               )
    ]
    def asdict(self):
        return struct_asdict(self)
    def __repr__(self):
        return repr(self.asdict())

class DISPLAYCONFIG_2DREGION(Structure):
    _fields_ = [
        ('cx', ctypes.c_uint32),
        ('cy', ctypes.c_uint32)
    ]
    def asdict(self):
        return struct_asdict(self)
    def __repr__(self):
        return repr(self.asdict())

class DISPLAYCONFIG_VIDEO_SIGNAL_INFO(Structure):
    _fields_ = [
        ('pixelRate'       , ctypes.c_uint64       ),
        ('hSyncFreq'       , DISPLAYCONFIG_RATIONAL),
        ('vSyncFreq'       , DISPLAYCONFIG_RATIONAL),
        ('activeSize'      , DISPLAYCONFIG_2DREGION),
        ('totalSize'       , DISPLAYCONFIG_2DREGION),
        ('videoStandard'   , ctypes.c_uint32       ),  # enum { uint32 videoStandard; uint6 vSyncFreqDivider; uint10 reserved }
        ('scanLineOrdering', ctypes.c_uint32       )   # enum DISPLAYCONFIG_SCANLINE_ORDERING
    ]
    def asdict(self):
        return struct_asdict(self)
    def __repr__(self):
        return repr(self.asdict())

class DISPLAYCONFIG_TARGET_MODE(Structure):
    _fields_ = [
        ('targetVideoSignalInfo', DISPLAYCONFIG_VIDEO_SIGNAL_INFO)
    ]
    def asdict(self):
        return struct_asdict(self)
    def __repr__(self):
        return repr(self.asdict())

class DISPLAYCONFIG_SOURCE_MODE(Structure):
    _fields_ = [
        ('width'      , ctypes.c_uint32),
        ('height'     , ctypes.c_uint32),
        ('pixelFormat', ctypes.c_uint32),  # enum DISPLAYCONFIG_PIXELFORMAT
        ('position'   , POINTL         )
    ]
    def asdict(self):
        return struct_asdict(self)
    def __repr__(self):
        return repr(self.asdict())

class DISPLAYCONFIG_DESKTOP_IMAGE_INFO(Structure):
    _fields_ = [
        ('PathSourceSize'    , POINTL),
        ('DesktopImageRegion', RECTL ),
        ('DesktopImageClip'  , RECTL )
    ]
    def asdict(self):
        return struct_asdict(self)
    def __repr__(self):
        return repr(self.asdict())

class DISPLAYCONFIG_MODE_INFO_UNION(Union):
    _fields_ = [
        ('targetMode'      , DISPLAYCONFIG_TARGET_MODE       ),
        ('sourceMode'      , DISPLAYCONFIG_SOURCE_MODE       ),
        ('desktopImageInfo', DISPLAYCONFIG_DESKTOP_IMAGE_INFO)
    ]
    def asdict(self):
        return struct_asdict(self)
    def __repr__(self):
        return repr(self.asdict())

class DISPLAYCONFIG_MODE_INFO(Structure):
    _fields_ = [
        ('infoType' , ctypes.c_uint32              ),  # enum DISPLAYCONFIG_MODE_INFO_TYPE
        ('id'       , ctypes.c_uint32              ),
        ('adapterId', LUID                         ),
        ('union'    , DISPLAYCONFIG_MODE_INFO_UNION)
    ]
    def asdict(self):
        return struct_asdict(self)
    def __repr__(self):
        return repr(self.asdict())


class DISPLAYCONFIG_DEVICE_INFO_HEADER(Structure):
    _fields_ = [
        ('type'     , ctypes.c_uint32),  # enum DISPLAYCONFIG_MODE_INFO_TYPE
        ('size'     , ctypes.c_uint32),
        ('adapterId', LUID           ),
        ('id'       , ctypes.c_uint32)
    ]
    def asdict(self):
        return struct_asdict(self)
    def __repr__(self):
        return repr(self.asdict())

class DISPLAYCONFIG_SOURCE_DEVICE_NAME(Structure):
    _fields_ = [
        ('header'           , DISPLAYCONFIG_DEVICE_INFO_HEADER),
        ('viewGdiDeviceName', WCHAR * CCHDEVICENAME           )
    ]
    def asdict(self):
        return struct_asdict(self)
    def __repr__(self):
        return repr(self.asdict())

class DISPLAYCONFIG_TARGET_DEVICE_NAME_FLAGS(ctypes.LittleEndianStructure):
    _fields_ = [
        ('friendlyNameFromEdid', ctypes.c_uint32, 1),
        ('friendlyNameForced', ctypes.c_uint32, 1),
        ('edidIdsValid', ctypes.c_uint32, 1),
    ]
    def asdict(self):
        return struct_asdict(self)
    def __repr__(self):
        return repr(self.asdict())

class DISPLAYCONFIG_TARGET_DEVICE_NAME(Structure):
    _fields_ = [
        ('header'                   , DISPLAYCONFIG_DEVICE_INFO_HEADER      ),
        ('flags'                    , DISPLAYCONFIG_TARGET_DEVICE_NAME_FLAGS),
        ('outputTechnology'         , ctypes.c_uint32                       ),  # enum DISPLAYCONFIG_VIDEO_OUTPUT_TECHNOLOGY
        ('edidManufactureId'        , ctypes.c_uint16                       ),
        ('edidProductCodeId'        , ctypes.c_uint16                       ),
        ('connectInstance'          , ctypes.c_uint32                       ),
        ('monitorFriendlyDeviceName', WCHAR * 64                            ),
        ('monitorDevicePath'        , WCHAR * 128                           )
    ]
    def asdict(self):
        return struct_asdict(self)
    def __repr__(self):
        return repr(self.asdict())


class DISPLAYCONFIG_ADAPTER_NAME(Structure):
    _fields_ = [
        ('header'           , DISPLAYCONFIG_DEVICE_INFO_HEADER),
        ('adapterDevicePath', WCHAR * 128                     )
    ]
    def asdict(self):
        return struct_asdict(self)
    def __repr__(self):
        return repr(self.asdict())



############
# Classes to abstract OS behaviour
GUID_DEVINTERFACE_MONITOR         = '{e6f07b5f-ee97-4a90-b076-33f57bf4eaa7}'
GUID_DEVINTERFACE_DISPLAY_ADAPTER = '{5b45201d-f2f2-4f3b-85bb-30ff1f953599}'

@dataclass(init=False)
class DisplayConfigPathInfo:
    source  : str
    target  : Dict[str, Any]
    monitor : DevicePath
    adapter : DevicePath

    def __init__(self, raw_path):
        super().__init__()

        self.source  = get_display_config_source_device_name(raw_path.sourceInfo.adapterId, raw_path.sourceInfo.id)

        self.target  = get_display_config_target_device_name(raw_path.targetInfo.adapterId, raw_path.targetInfo.id)
        self.monitor = DevicePath(str(self.target['monitorDevicePath']))
        if self.monitor.type != 'DISPLAY':
            raise ValueError(f"Expected target.monitorDevicePath to have type 'DISPLAY', got '{self.monitor['display']}' instead")
        if self.monitor.guid != GUID_DEVINTERFACE_MONITOR:
            raise ValueError(f"Expected target.monitorDevicePath to have GUID 'GUID_DEVINTERFACE_MONITOR', got '{self.monitor['guid']}' instead")

        adapter_path = get_display_config_adapter_name(raw_path.targetInfo.adapterId, raw_path.targetInfo.id)
        self.adapter = DevicePath(adapter_path)
        if self.adapter.guid != GUID_DEVINTERFACE_DISPLAY_ADAPTER:
            raise ValueError(f"Expected target.monitorDevicePath to have GUID 'GUID_DEVINTERFACE_MONITOR', got '{self.adapter['guid']}' instead")


############
# Implementation
def win32_display_config_get_device_info(adapter_id : LUID, source_id : ctypes.c_uint32, request_cls):
    if request_cls is DISPLAYCONFIG_SOURCE_DEVICE_NAME:
        request_type = 0x1  # DISPLAYCONFIG_DEVICE_INFO_GET_SOURCE_NAME
    elif request_cls is DISPLAYCONFIG_TARGET_DEVICE_NAME:
        request_type = 0x2  # DISPLAYCONFIG_DEVICE_INFO_GET_TARGET_NAME
    elif request_cls is DISPLAYCONFIG_ADAPTER_NAME:
        request_type = 0x4  # DISPLAYCONFIG_DEVICE_INFO_GET_ADAPTER_NAME
    else:
        raise ValueError(f"Unsupported request_cls='{request_cls.__name__}'")

    request = request_cls()
    request.header.size = sizeof(request)
    request.header.adapterId = adapter_id
    request.header.id = source_id
    request.header.type = request_type

    errno = windll.user32.DisplayConfigGetDeviceInfo(byref(request))
    if errno != 0:
        raise WinError(errno)

    # log.debug(f"Result: {struct_asdict(request)}")
    return request


def get_display_config_source_device_name(adapter_id, source_id):
    request = win32_display_config_get_device_info(adapter_id, source_id, DISPLAYCONFIG_SOURCE_DEVICE_NAME)
    return request.viewGdiDeviceName

def get_display_config_target_device_name(adapter_id, source_id):
    request = win32_display_config_get_device_info(adapter_id, source_id, DISPLAYCONFIG_TARGET_DEVICE_NAME)
    result = request.asdict()
    del result['header']
    return result

def get_display_config_adapter_name(adapter_id, source_id):
    request = win32_display_config_get_device_info(adapter_id, source_id, DISPLAYCONFIG_ADAPTER_NAME)
    return request.adapterDevicePath



def _handle_display_config_paths(paths, num_paths):
    paths_arr = []

    for i in range(0, num_paths.value):
        path = paths[i]
        paths_arr.append(DisplayConfigPathInfo(path))

    return paths_arr


def _handle_display_config_modes(modes, num_modes, copy=False):
    modes_arr = []

    for i in range(0, num_modes.value):
        mode = modes[i]
        info_type = mode.infoType

        if info_type == 1:  # DISPLAYCONFIG_MODE_INFO_TYPE_SOURCE
            typ = 'source'
            device = get_display_config_source_device_name(mode.adapterId, mode.id)
        elif info_type == 2:  # DISPLAYCONFIG_MODE_INFO_TYPE_TARGET
            typ = 'target'
            device = get_display_config_target_device_name(mode.adapterId, mode.id)
        else:
            raise RuntimeError(f"Unexpected mode.infoType={info_type}")

        adapter = get_display_config_adapter_name(mode.adapterId, mode.id)

        # Copy information into return result
        d = {'type': typ, 'device': device, 'adapter': adapter}

        if copy:
            copied = DISPLAYCONFIG_MODE_INFO()
            ctypes.memmove(byref(copied), byref(mode), sizeof(copied))
            d['mode'] = copied

        modes_arr.append(d)

    return modes_arr



QDC_ALL_PATHS         = ctypes.c_uint32(0x1)
QDC_ONLY_ACTIVE_PATHS = ctypes.c_uint32(0x2)
QDC_DATABASE_CURRENT  = ctypes.c_uint32(0x4)

def query_display_config(flags=QDC_ONLY_ACTIVE_PATHS, paths_only=False, modes_only=False):
    num_paths = ctypes.c_uint32()
    num_modes = ctypes.c_uint32()

    # Note: We loop here since the monitor config could change, and thus the buffer size is incorrect
    i = 0
    while True:
        i += 1

        # Get buffer sizes
        errno = windll.user32.GetDisplayConfigBufferSizes(flags, byref(num_paths), byref(num_modes))
        if errno != 0:
            raise WinError(errno)
        # log.debug(f"1: num_paths={num_paths.value}, num_modes={num_modes.value}")

        # Query Display Config
        paths = (DISPLAYCONFIG_PATH_INFO * num_paths.value)()
        modes = (DISPLAYCONFIG_MODE_INFO * num_modes.value)()

        topologyId = None
        if flags.value == QDC_DATABASE_CURRENT.value:
            topologyId = ctypes.c_uint32()

        errno = windll.user32.QueryDisplayConfig(flags, byref(num_paths), byref(paths), byref(num_modes), byref(modes), None if topologyId is None else byref(topologyId))
        if errno != 0:
            if i < 1:
                errnum = GetLastError()
                if errnum == 122:  # ERROR_INSUFFICIENT_BUFFER
                    i -= 1
                    continue
            raise WinError(errno)

        break
    # log.debug(f"2: num_paths={num_paths.value}, num_modes={num_modes.value}, topologyId={None if topologyId is None else topologyId.value}")

    # Return results
    res_paths = None
    res_modes = None

    if not modes_only:
        res_paths = _handle_display_config_paths(paths, num_paths)
    if not paths_only:
        res_modes = _handle_display_config_modes(modes, num_modes)

    if paths_only:
        return res_paths
    elif modes_only:
        return res_modes
    else:
        return {'paths': res_paths, 'modes': res_modes}