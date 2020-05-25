# SPDX-License-Identifier: GPLv3-or-later
# Copyright © 2020 pyddcci Rui Pinheiro

from abc import abstractmethod, ABC

from ..monitor_info import BaseOsMonitorInfo

from .api import display_config, display_devices
from .api.edid import edid_from_monitor_model_and_uid, OSEdidError
from ...edid import Edid

from . import getLogger
log = getLogger(__name__)


########
# OS Monitor Information
class WindowsOsMonitorInfo(BaseOsMonitorInfo):
    """
    Windows implementation of BaseOsMonitorInfo
    """

    __slots__ = BaseOsMonitorInfo.__slots__


    # Initialization
    def __init__(self, dcp_info):
        # Initialize adapter device
        adapter_device_name = str(dcp_info.source)
        adapter_device_name_prefix = r'\\.\DISPLAY'
        assert(adapter_device_name.startswith(adapter_device_name_prefix))
        adapter_device_number = int(adapter_device_name[len(adapter_device_name_prefix):])
        adapter_device = self.__class__.Device(parent=self, name=adapter_device_name, number=adapter_device_number, id=dcp_info.adapter['devid'])

        # Initialize adapter
        adapter_d = dict(dcp_info.adapter)
        del adapter_d['devid']
        adapter_d['device'] = adapter_device

        adapter = self.__class__.Adapter(**adapter_d)

        # Initialize monitor
        monitor_device = self.__class__.Device(parent=self, id=fr"MONITOR\{dcp_info.monitor['devid']}")

        monitor_d = dict(dcp_info.monitor)
        monitor_d['model'] = monitor_d['devid']
        del monitor_d['devid']
        monitor_d['device'] = monitor_device

        monitor = self.__class__.Monitor(**monitor_d)

        if dcp_info.target['flags']['edidIdsValid']:
            monitor.manufacturer_id = Edid.parse_manufacture_id(dcp_info.target['edidManufactureId'], swap=True)
            monitor.product_id      = Edid.parse_product_id(dcp_info.target['edidProductCodeId'], swap=True)

        if dcp_info.target['flags']['friendlyNameFromEdid'] and not dcp_info.target['flags']['friendlyNameForced']:
            monitor.name = str(dcp_info.target['monitorFriendlyDeviceName'])

        # Call superclass
        super().__init__(adapter, monitor)


    def _post_initialize(self):
        super()._post_initialize()

        self._read_edid()
        self._read_GetMonitorInfo_adapter()
        self._read_GetMonitorInfo_monitor()


    # Edid
    def _read_edid(self):
        try:
            edid = edid_from_monitor_model_and_uid(self.monitor.model, self.monitor.uid)
        except OSEdidError:
            self.log.warn(f"Could not find EDID")
            return

        # Copy interesting data
        def _copy_from_edid(attr1, attr2=None):
            if attr2 is None:
                attr2 = attr1

            self_attr = getattr(self.monitor, attr1)
            edid_attr = edid[attr2]

            if self_attr is not None:
                if self_attr != edid_attr:
                    raise RuntimeError(f"Had {attr1}='{self_attr}' but got EDID.{attr2}='{edid_attr}'")
            else:
                setattr(self.monitor, attr1, edid_attr)

        _copy_from_edid('manufacturer_id')
        _copy_from_edid('product_id')
        _copy_from_edid('name', 'display_name')
        _copy_from_edid('serial', 'serial_string')


    # GetMonitorInfo
    def _read_GetMonitorInfo_adapter(self):
        res = display_devices.win32_enum_display_devices_w(None, self.adapter.device.number - 1)

        # Sanity checks
        def _assert_matches(attr_x, x, attr_y, y):
            if x != str(y):
                raise RuntimeError(f"Had {attr_x}='{x}', but got res.{attr_y}='{y}'")

        _assert_matches('adapter.device.name', self.adapter.device.name, 'DeviceName', res.DeviceName)
        _assert_matches('adapter', fr"{self.adapter.type}\{self.adapter.device.id}", 'DeviceID', res.DeviceID)

        # Copy interesting data
        def _copy(obj, attr_x, y):
            x = obj[attr_x]
            if x is not None and x != y:
                raise RuntimeError(f"Had {attr_x}='{x}', but got '{y}'")
            obj[attr_x] = y

        _copy(self.adapter, 'model', str(res.DeviceString))
        _copy(self.adapter, 'primary', res.primary)

    def _read_GetMonitorInfo_monitor(self):
        res = display_devices.win32_enum_display_devices_w(self.adapter.device.name, 0)
        assert(display_devices.win32_enum_display_devices_w(self.adapter.device.name, 1) is None)

        # Sanity checks
        def _assert_startswith(x, attr_y, y):
            if not str(y).startswith(x):
                raise RuntimeError(f"Expected res.{attr_y} to start with '{x}', but got '{y}'")

        device_name_prefix = fr"{self.adapter.device.name}\Monitor"
        _assert_startswith(device_name_prefix, 'DeviceName', res.DeviceName)
        _assert_startswith(self.monitor.device.id, 'DeviceName', res.DeviceID)

        # Copy interesting data
        def _copy(obj, attr_x, y):
            x = obj[attr_x]
            if x is not None and x != y:
                raise RuntimeError(f"Had {attr_x}='{x}', but got '{y}'")
            obj[attr_x] = y

        _copy(self.monitor.device, 'name', str(res.DeviceName))
        _copy(self.monitor.device, 'number', int(self.monitor.device.name[len(device_name_prefix):]))


    # Enumerate monitors
    @classmethod
    def enumerate(cls):
        paths = display_config.query_display_config(paths_only=True)

        ret = []
        for path in paths:
            info = cls(path)
            ret.append(info)

        return ret